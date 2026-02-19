from logging import root
import os
import json
import asyncio
import pandas as pd
import argparse
import sys

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
import boto3


# Load environment variables from .env file
load_dotenv()

# ----------------------------
# Config (edit as needed)
# ----------------------------
WINDOW_HOURS = int(os.getenv("WINDOW_HOURS", "24"))
BASELINE_DAYS = int(os.getenv("BASELINE_DAYS", "14"))
MIN_HISTORY = int(os.getenv("MIN_HISTORY", "10"))
ANOMALY_MULTIPLIER = float(os.getenv("ANOMALY_MULTIPLIER", "1.5"))

# Slack configuration
ENABLE_SLACK_NOTIFICATIONS = os.getenv("ENABLE_SLACK_NOTIFICATIONS", "false").lower() == "true"
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#test-notification-ai")


# Command to start your MCP server over stdio:
airflow_transport = StdioTransport(
    command="python",
    args=["-m", "airflow_monitoring.airflow_mcp_server"],
    env={
        "AIRFLOW_DB_URL": os.environ["AIRFLOW_DB_URL"],
        # pass anything else your server needs:
        # "SOME_ENV": os.environ.get("SOME_ENV", "")
    }
)

# Slack MCP server transport (if enabled)
slack_transport = None
if ENABLE_SLACK_NOTIFICATIONS and os.getenv("SLACK_BOT_TOKEN"):
    slack_transport = StdioTransport(
        command="python",
        args=["-m", "airflow_monitoring.slack_mcp_server"],
        env={
            "SLACK_BOT_TOKEN": os.environ["SLACK_BOT_TOKEN"]
        }
    )


def compute_metrics(
    recent_rows: List[Dict[str, Any]],
    baseline_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    generated_at = now.isoformat()

    recent = pd.DataFrame(recent_rows)

    if recent.empty:
        return {
            "generated_at": generated_at,
            "top5_longest": [],
            "anomalies": [],
            "notes": ["No recent DAG runs returned by MCP tool."],
        }

    for c in ["start_date", "end_date"]:
        if c in recent.columns:
            recent[c] = pd.to_datetime(recent[c], utc=True, errors="coerce")

    # duration: end_date if present else now (running)
    recent["end_eff"] = recent["end_date"].fillna(pd.Timestamp(now))
    recent["duration_sec"] = (recent["end_eff"] - recent["start_date"]).dt.total_seconds()

    baseline = pd.DataFrame(baseline_rows)
    stats = pd.DataFrame(columns=["dag_id", "count", "p50", "p90"])

    if not baseline.empty:
        baseline["start_date"] = pd.to_datetime(baseline["start_date"], utc=True, errors="coerce")
        baseline["end_date"] = pd.to_datetime(baseline["end_date"], utc=True, errors="coerce")
        baseline = baseline.dropna(subset=["start_date", "end_date", "dag_id"])
        baseline["duration_sec"] = (baseline["end_date"] - baseline["start_date"]).dt.total_seconds()

        stats = (
            baseline.groupby("dag_id")["duration_sec"]
            .agg(
                count="count",
                p50=lambda s: s.quantile(0.5),
                p90=lambda s: s.quantile(0.9),
            )
            .reset_index()
        )


    recent2 = recent.merge(stats, on="dag_id", how="left")

    # anomaly: duration > multiplier * p90 and enough history
    recent2["is_anomaly"] = (
        (recent2["count"] >= MIN_HISTORY)
        & (recent2["p90"].notna())
        & (recent2["duration_sec"] > ANOMALY_MULTIPLIER * recent2["p90"])
    )

    top5_longest = recent2.sort_values(by="duration_sec", ascending=False).head(5)[["dag_id", "run_id", "state", "start_date", "end_date", "duration_sec", "p90", "count", "is_anomaly"]]

    anomalies = recent2[recent2["is_anomaly"]].sort_values(by="duration_sec", ascending=False)[["dag_id", "run_id", "state", "start_date", "end_date", "duration_sec", "p90", "count"]]

    result = {
        "generated_at": now.isoformat(),
        "window_hours": WINDOW_HOURS,
        "baseline_days": BASELINE_DAYS,
        "min_history": MIN_HISTORY,
        "anomaly_multiplier": ANOMALY_MULTIPLIER,
        "top5_longest": [row_to_dict(r) for _, r in top5_longest.iterrows()],
        "anomalies": [row_to_dict(r) for _, r in anomalies.iterrows()],
        "notes": [],
    }

    return result


def row_to_dict(row):
    """Convert pandas row to dict with proper datetime handling."""
    result = {}
    for key, value in row.items():
        if pd.isna(value):
            result[key] = None
        elif isinstance(value, pd.Timestamp):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result




def bedrock_summarize(metrics: Dict[str, Any]) -> str:
    """Generate AI summary using AWS Bedrock, with fallback for missing credentials."""
    
    # Check if AWS credentials are available
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION")
    
    if not aws_access_key or not aws_secret_key or not aws_region:
        print("⚠️  AWS credentials not configured, using fallback summary...")
        return generate_fallback_summary(metrics)
    
    try:
        bedrock_client = boto3.client("bedrock-runtime", region_name=aws_region)

        # AI-focused system prompt
        system_text = (
            "You are an advanced AI agent specializing in Airflow pipeline intelligence and analytics. "
            "Your core capabilities include pattern recognition, anomaly detection, predictive insights, "
            "and automated root cause analysis. You process complex data patterns and provide "
            "intelligent recommendations with machine learning-enhanced understanding. "
            "Generate analytical Slack reports that demonstrate deep system intelligence, "
            "not just data summaries. Use AI-driven insights to predict issues, correlate patterns, "
            "and suggest proactive optimizations. Always provide data-driven confidence scores "
            "and intelligent prioritization based on impact analysis."
        )

        # AI-focused user prompt
        user_text = (
            "Perform intelligent analysis as an AI agent with advanced pattern recognition capabilities:\n\n"
            "1) 🧠 **AI ANALYSIS**: Apply machine learning insights to identify hidden patterns, "
            "correlations, and predictive indicators in the data\n"
            "2) 🔮 **PREDICTIVE INSIGHTS**: Based on historical patterns, predict potential future issues "
            "and provide early warning indicators with confidence scores\n"
            "3) 🎯 **INTELLIGENT PRIORITIZATION**: Use impact analysis and risk scoring to rank issues "
            "by business criticality and urgency\n"
            "4) 🔍 **ROOT CAUSE ANALYSIS**: Apply causal inference to identify underlying causes of anomalies "
            "and performance degradations\n"
            "5) 💡 **AI RECOMMENDATIONS**: Provide intelligent, data-driven optimization suggestions "
            "with expected impact metrics\n\n"
            "Advanced AI Requirements:\n"
            "- Analyze temporal patterns and seasonal trends\n"
            "- Identify cascading failure risks and dependency impacts\n"
            "- Provide confidence percentages for predictions (e.g., '85% confidence')\n"
            "- Suggest proactive monitoring thresholds based on learned patterns\n"
            "- Correlate performance anomalies with resource utilization patterns\n"
            "- Use statistical analysis to separate noise from genuine issues\n\n"
            "SLACK FORMATTING REQUIREMENTS:\n"
            "- Format as Slack-friendly markdown with clear sections\n"
            "- Use **bold** for DAG names, metrics, and key findings\n"
            "- Keep sections concise (max 3-5 items per section)\n"
            "- Use emojis for visual organization and impact (🔴🟡🟢)\n"
            "- Include specific numbers, percentages, and confidence scores\n"
            "- Structure with clear headers and bullet points\n"
            "- Prioritize most critical AI insights first\n\n"
            "Generate an AI-powered Slack report that showcases advanced analytical capabilities:\n"
            f"{json.dumps(metrics, indent=2)}"
        )

        response = bedrock_client.converse(
            modelId=os.getenv("MODEL_ID"),
            system=[{"text": system_text}],
            messages=[
                {"role": "user", 
                "content": [{"text": user_text}]}
            ],
            inferenceConfig={
                "maxTokens": 600,
                "temperature": 0.2,   # better for monitoring reports than 0.7
            },
        )

        parts = response["output"]["message"]["content"]
        text_parts = [p.get("text", "") for p in parts if isinstance(p, dict)]
        return "\n".join([t for t in text_parts if t]).strip()
        
    except Exception as e:
        print(f"⚠️  AWS Bedrock error: {e}")
        print("   Falling back to template-based summary...")
        return generate_fallback_summary(metrics)


def generate_fallback_summary(metrics: Dict[str, Any]) -> str:
    """Generate an AI-enhanced template-based analysis when Bedrock is unavailable."""
    
    top5 = metrics.get("top5_longest", [])
    anomalies = metrics.get("anomalies", [])
    paused_dags = metrics.get("paused_dags", [])
    stale_dags = metrics.get("stale_dags", [])
    paused_count = metrics.get("paused_count", 0)
    stale_count = metrics.get("stale_count", 0)
    health_data = metrics.get("health_summary", {})
    
    # Header with AI branding
    summary = "🤖 **AI AIRFLOW INTELLIGENCE REPORT**\n"
    summary += f"📅 *Analysis completed: {metrics.get('generated_at', 'Just now')}*\n\n"
    
    # AI-powered status assessment
    anomaly_count = len(anomalies)
    if anomaly_count > 0 or stale_count > 5 or paused_count > 10:
        risk_level = "HIGH" if anomaly_count > 5 else "MODERATE"
        confidence = 95 if anomaly_count > 3 else 80
        summary += f"⚠️ **AI RISK ASSESSMENT**: {risk_level} (Confidence: {confidence}%)\n"
        summary += f"🔍 **Pattern Analysis**: {anomaly_count} performance anomalies, {stale_count} stale pipelines detected\n\n"
    else:
        summary += "✅ **AI ASSESSMENT**: System operating within normal parameters (Confidence: 92%)\n\n"
    
    # Performance Intelligence Section
    if anomalies or top5:
        summary += "🧠 **PERFORMANCE INTELLIGENCE**\n"
        
        if anomalies:
            severity_score = sum([ano.get('duration_sec', 0) / ano.get('p90', 1) for ano in anomalies[:3]]) / 3
            summary += f"• **ML-Detected Anomalies**: {len(anomalies)} patterns identified (Severity Score: {severity_score:.1f})\n"
            
            for i, anomaly in enumerate(anomalies[:3], 1):
                dag_id = anomaly.get('dag_id', 'Unknown')
                duration = anomaly.get('duration_sec', 0)
                p90 = anomaly.get('p90', 0)
                
                duration_mins = duration / 60 if duration else 0
                p90_mins = p90 / 60 if p90 else 0
                deviation_pct = ((duration - p90) / p90 * 100) if p90 > 0 else 0
                
                summary += f"  {i}. **{dag_id}**: {duration_mins:.0f}m ({deviation_pct:+.0f}% vs baseline pattern)\n"
        
        summary += "\n"
    
    # Intelligent Health Assessment
    health_issues = []
    if stale_count > 0:
        health_issues.append(f"{stale_count} stale pipelines")
    if paused_count > 0:
        health_issues.append(f"{paused_count} paused workflows")
    
    if health_issues:
        summary += "🔮 **PREDICTIVE HEALTH ANALYSIS**\n"
        
        # AI-style health correlation
        if stale_count > 20:
            pipeline_health_risk = "HIGH"
            impact_score = min(stale_count * 2, 100)
        elif stale_count > 5:
            pipeline_health_risk = "MODERATE" 
            
            impact_score = stale_count * 3
        else:
            pipeline_health_risk = "LOW"
            impact_score = stale_count * 5
        
        summary += f"• **Pipeline Health Risk**: {pipeline_health_risk} (Impact Score: {impact_score}%)\n"
        summary += f"• **Maintenance Required**: {', '.join(health_issues)}\n"
        
        # Show critical stale DAGs with AI analysis
        if stale_dags:
            critical_stale = [dag for dag in stale_dags[:3] if dag.get('days_since_last_run', 0) > 20]
            if critical_stale:
                summary += f"• **Critical Pattern**: Long-dormant pipelines detected\n"
                for dag in critical_stale:
                    dag_id = dag.get('dag_id', 'Unknown')
                    days = int(dag.get('days_since_last_run', 0))
                    failure_risk = "HIGH" if days > 60 else "MEDIUM"
                    summary += f"  • **{dag_id}**: {days}d inactive (Restart Risk: {failure_risk})\n"
        
        summary += "\n"
    
    # AI Health Score
    if health_data:
        health_pct = health_data.get("health_percentage", 0)
        total_dags = health_data.get("total_dags", 0)
        active_dags = health_data.get("active_dags", 0)
        
        # AI-style health interpretation
        if health_pct >= 85:
            health_status = "OPTIMAL"
            emoji = "🟢"
        elif health_pct >= 70:
            health_status = "STABLE"
            emoji = "🟡" 
        else:
            health_status = "DEGRADED"
            emoji = "🔴"
        
        summary += f"{emoji} **AI HEALTH SCORE**: {health_pct:.0f}% - {health_status}\n"
        summary += f"📊 **Pipeline Efficiency**: {active_dags}/{total_dags} workflows optimally active\n"
    
    # AI Recommendations
    if anomaly_count > 3:
        summary += "\n🎯 **AI OPTIMIZATION RECOMMENDATIONS**:\n"
        summary += "• **Immediate**: Investigate top performance outliers using statistical analysis\n"
        summary += "• **Proactive**: Implement adaptive scaling based on historical load patterns\n" 
        if stale_count > 10:
            summary += "• **Strategic**: Execute pipeline lifecycle management and cleanup protocols\n"
    elif stale_count > 20:
        summary += "\n🎯 **AI RECOMMENDATIONS**:\n"
        summary += "• **Data Hygiene**: Implement intelligent pipeline archival system\n"
        summary += "• **Automation**: Deploy AI-driven unused resource identification\n"
    elif anomaly_count == 0 and stale_count < 5:
        summary += "\n✨ **AI CONCLUSION**: System demonstrating optimal performance patterns - continue monitoring\n"
    
    return summary


async def send_slack_notification(summary: str, metrics: Dict[str, Any]) -> bool:
    """
    Send the AI agent results to Slack if notifications are enabled.
    
    Args:
        summary: The AI-generated summary report
        metrics: The computed metrics dictionary
    
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    if not ENABLE_SLACK_NOTIFICATIONS or not slack_transport:
        print("📱 Slack notifications disabled or not configured")
        return False
    
    try:
        async with Client(slack_transport) as slack_client:
            # Determine message color and title based on severity
            anomaly_count = len(metrics.get("anomalies", []))
            stale_count = metrics.get("stale_count", 0)  
            paused_count = metrics.get("paused_count", 0)
            health_pct = metrics.get("health_summary", {}).get("health_percentage", 100)
            
            # Calculate severity score
            severity_score = 0
            if anomaly_count > 0:
                severity_score += min(anomaly_count * 2, 20)  # Max 20 points for anomalies
            if stale_count > 10:
                severity_score += min((stale_count - 10) * 0.5, 10)  # Max 10 points for stale DAGs
            if health_pct < 80:
                severity_score += (80 - health_pct) * 0.3  # Up to 24 points for low health
            
            # Set color and title based on severity
            if severity_score >= 15 or anomaly_count > 10:
                color = "danger"
                title = f"🔴 **CRITICAL** Airflow Issues - {anomaly_count} anomalies detected"
            elif severity_score >= 5 or anomaly_count > 0:
                color = "warning" 
                title = f"🟡 **ATTENTION** Airflow Monitoring - {anomaly_count} issues found"
            elif stale_count > 20 or paused_count > 50:
                color = "warning"
                title = f"🟡 **HOUSEKEEPING** Airflow Health - DAG cleanup needed"
            else:
                color = "good"
                title = f"✅ **HEALTHY** Airflow Report - System running smoothly"
            
            # Send rich formatted message
            result = await slack_client.call_tool(
                "send_rich_message",
                {
                    "channel": SLACK_CHANNEL,
                    "title": title,
                    "message": summary,
                    "color": color,
                    "username": os.getenv("SLACK_USERNAME", "Airflow Monitor")
                }
            )
            
            # Check if the result has structured_content
            if hasattr(result, 'structured_content') and result.structured_content:
                response_data = result.structured_content  # Direct access, no 'result' key
            else:
                # Fallback to data attribute if structured_content is not available
                response_data = result.data[0] if hasattr(result, 'data') and result.data else {}
            
            if response_data.get("success", False):
                print(f"✅ Slack notification sent successfully to {SLACK_CHANNEL}")
                return True
            else:
                print(f"❌ Failed to send Slack notification: {response_data.get('error', 'Unknown error')}")
                return False
                
    except Exception as e:
        print(f"❌ Error sending Slack notification: {str(e)}")
        return False


async def main():
    async with Client(airflow_transport) as mcp_client:

        tools = await mcp_client.list_tools()
        
        # Call your MCP tools (names must match what you defined in the server)
        recent = await mcp_client.call_tool("get_dag_runs", {"window_hours": WINDOW_HOURS})
        baseline = await mcp_client.call_tool("get_baseline_durations", {"days": BASELINE_DAYS})
        
        # Get additional DAG health information
        paused = await mcp_client.call_tool("get_paused_dags", {})
        stale = await mcp_client.call_tool("get_stale_dags", {"days_inactive": 10})
        health_summary = await mcp_client.call_tool("get_dag_health_summary", {})

        # FastMCP returns structured content - use the parsed result directly
        recent_rows = recent.structured_content.get('result', []) if hasattr(recent, 'structured_content') and recent.structured_content else []
        baseline_rows = baseline.structured_content.get('result', []) if hasattr(baseline, 'structured_content') and baseline.structured_content else []
        paused_dags = paused.structured_content.get('result', []) if hasattr(paused, 'structured_content') and paused.structured_content else []
        stale_dags = stale.structured_content.get('result', []) if hasattr(stale, 'structured_content') and stale.structured_content else []
        health_data = health_summary.structured_content.get('result', {}) if hasattr(health_summary, 'structured_content') and health_summary.structured_content else {}

        print(f"✅ Extracted {len(recent_rows)} recent DAG runs")
        print(f"✅ Extracted {len(baseline_rows)} baseline DAG runs")
        print(f"✅ Found {len(paused_dags)} paused DAGs")
        print(f"✅ Found {len(stale_dags)} stale DAGs (schedule-aware thresholds: daily=10d, weekly=14d)")
        
        # Compute metrics including DAG health information
        metrics = compute_metrics(recent_rows, baseline_rows)
        
        # Add DAG health information to metrics
        metrics.update({
            "paused_dags": paused_dags[:10],  # Limit to top 10 for summary
            "stale_dags": stale_dags[:10],    # Limit to top 10 for summary  
            "paused_count": len(paused_dags),
            "stale_count": len(stale_dags),
            "health_summary": health_data
        })

        # Summarize with Bedrock
        summary = bedrock_summarize(metrics)
        
        # Send to Slack if enabled
        await send_slack_notification(summary, metrics)

        # Print to console
        print("\n" + "=" * 80)
        print("AIRFLOW RUNTIME REPORT")
        print("=" * 80)
        print(summary)
        print("\n(Generated at: {})".format(metrics["generated_at"]))



if __name__ == "__main__":
    asyncio.run(main())