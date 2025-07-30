#!/bin/bash

# Monitor CI script for homebrew-folder2md4llms
# This script monitors the GitHub Actions workflows and provides real-time status updates

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "failure")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "in_progress")
            echo -e "${YELLOW}⏳ $message${NC}"
            ;;
        "queued")
            echo -e "${BLUE}📋 $message${NC}"
            ;;
        *)
            echo -e "${NC}$message${NC}"
            ;;
    esac
}

# Function to get workflow status
get_workflow_status() {
    gh run list --limit 5 --json status,conclusion,name,createdAt,workflowName,headSha
}

# Function to monitor workflows
monitor_workflows() {
    echo "🔍 Monitoring GitHub Actions workflows for homebrew-folder2md4llms..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    while true; do
        clear
        echo "📊 Workflow Status Monitor - $(date)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Get latest runs
        runs=$(gh run list --limit 10 --json status,conclusion,name,createdAt,workflowName,headSha,url)
        
        # Parse and display runs
        echo "$runs" | jq -r '.[] | "\(.status)|\(.conclusion)|\(.workflowName)|\(.name)|\(.createdAt)|\(.url)"' | head -10 | while IFS='|' read -r status conclusion workflow_name name created_at url; do
            if [[ "$status" == "in_progress" ]]; then
                print_status "in_progress" "$workflow_name: $name (Running...)"
            elif [[ "$status" == "queued" ]]; then
                print_status "queued" "$workflow_name: $name (Queued)"
            elif [[ "$status" == "completed" ]]; then
                if [[ "$conclusion" == "success" ]]; then
                    print_status "success" "$workflow_name: $name"
                else
                    print_status "failure" "$workflow_name: $name"
                fi
            fi
        done
        
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Check if all workflows are completed
        in_progress_count=$(echo "$runs" | jq -r '.[] | select(.status == "in_progress") | .workflowName' | head -3 | wc -l)
        queued_count=$(echo "$runs" | jq -r '.[] | select(.status == "queued") | .workflowName' | head -3 | wc -l)
        
        if [[ $in_progress_count -eq 0 && $queued_count -eq 0 ]]; then
            echo ""
            echo "🎉 All workflows completed!"
            
            # Show summary of latest runs
            echo ""
            echo "📋 Latest Results Summary:"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            
            # Get the latest commit's runs
            latest_commit=$(gh run list --limit 1 --json headSha | jq -r '.[0].headSha')
            latest_runs=$(gh run list --limit 20 --json status,conclusion,workflowName,headSha | jq -r --arg commit "$latest_commit" '.[] | select(.headSha == $commit) | "\(.conclusion)|\(.workflowName)"')
            
            ci_status=""
            test_formula_status=""
            test_installation_status=""
            
            while IFS='|' read -r conclusion workflow_name; do
                case $workflow_name in
                    "CI")
                        ci_status=$conclusion
                        ;;
                    "Test Formula")
                        test_formula_status=$conclusion
                        ;;
                    "Test Installation")
                        test_installation_status=$conclusion
                        ;;
                esac
            done <<< "$latest_runs"
            
            print_status "$ci_status" "CI Workflow: $ci_status"
            print_status "$test_formula_status" "Test Formula Workflow: $test_formula_status"
            print_status "$test_installation_status" "Test Installation Workflow: $test_installation_status"
            
            echo ""
            if [[ "$ci_status" == "success" && "$test_formula_status" == "success" && "$test_installation_status" == "success" ]]; then
                echo -e "${GREEN}🎊 All workflows PASSED! 🎊${NC}"
            else
                echo -e "${RED}⚠️  Some workflows failed. Check the logs for details.${NC}"
            fi
            
            break
        fi
        
        echo "🔄 Refreshing in 10 seconds... (Press Ctrl+C to stop)"
        sleep 10
    done
}

# Function to show workflow logs
show_logs() {
    echo "📋 Recent workflow runs:"
    gh run list --limit 5
    echo ""
    echo "🔍 To view logs for a specific run, use:"
    echo "gh run view <run-id> --log"
    echo ""
    echo "🔍 To view failed logs only:"
    echo "gh run view <run-id> --log-failed"
}

# Main script
case ${1:-monitor} in
    "monitor")
        monitor_workflows
        ;;
    "logs")
        show_logs
        ;;
    "status")
        echo "📊 Current workflow status:"
        gh run list --limit 5
        ;;
    "help")
        echo "Usage: $0 [monitor|logs|status|help]"
        echo "  monitor  - Monitor workflows in real-time (default)"
        echo "  logs     - Show recent runs and log commands"
        echo "  status   - Show current status"
        echo "  help     - Show this help message"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac