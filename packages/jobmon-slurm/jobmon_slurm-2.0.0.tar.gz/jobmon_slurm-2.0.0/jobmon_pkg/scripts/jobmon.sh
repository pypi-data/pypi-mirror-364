#!/bin/bash
# Enhanced Universal SLURM Job Monitor
# Version 2.0 - Robust pattern matching and job completion detection
# Usage: jobmon [job_pattern] [options]

# Default values
JOB_PATTERN=""
TARGET_USER=$(whoami)
QUIET_MODE=false
REFRESH_INTERVAL=10
HELP_MODE=false
DEBUG_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--user)
            TARGET_USER="$2"
            shift 2
            ;;
        -q|--quiet)
            QUIET_MODE=true
            shift
            ;;
        -i|--interval)
            REFRESH_INTERVAL="$2"
            shift 2
            ;;
        -d|--debug)
            DEBUG_MODE=true
            shift
            ;;
        -h|--help)
            HELP_MODE=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            HELP_MODE=true
            shift
            ;;
        *)
            if [[ -z "$JOB_PATTERN" ]]; then
                JOB_PATTERN="$1"
            else
                echo "Multiple job patterns not supported: $1"
                HELP_MODE=true
            fi
            shift
            ;;
    esac
done

# Debug function
debug_log() {
    if [[ "$DEBUG_MODE" == true ]]; then
        echo "[DEBUG] $1" >&2
    fi
}

# Help function
show_help() {
    cat << EOF
Enhanced Universal SLURM Job Monitor v2.0

Usage: jobmon [job_pattern] [options]

Arguments:
  job_pattern    Job name pattern or job ID to monitor (default: all jobs)

Options:
  -u, --user     Monitor jobs for specific user (default: current user)
  -q, --quiet    Quiet mode - less verbose output
  -i, --interval Set refresh interval in seconds (default: 10)
  -d, --debug    Enable debug output for troubleshooting
  -h, --help     Show this help message

Examples:
  jobmon                    Monitor all your jobs
  jobmon foldx             Monitor jobs matching "foldx"
  jobmon dual_env_audit    Monitor jobs (handles SLURM name truncation)
  jobmon 41004010          Monitor specific job ID
  jobmon -u alice          Monitor alice's jobs
  jobmon foldx -q          Monitor foldx jobs in quiet mode
  jobmon -i 5              Monitor with 5-second refresh
  
New Features v2.0:
  ✅ Smart pattern matching (handles SLURM job name truncation)
  ✅ Job completion detection using sacct
  ✅ Better feedback when jobs finish quickly
  ✅ Progressive pattern fallback strategies
  ✅ Helpful suggestions for failed searches
  
Controls:
  Ctrl+C                   Exit monitoring
EOF
}

if [[ "$HELP_MODE" == true ]]; then
    show_help
    exit 0
fi

# Enhanced function to find matching jobs with progressive pattern matching
find_matching_jobs_enhanced() {
    local pattern="$1"
    local results=""
    
    debug_log "Searching for pattern: '$pattern'"
    
    if [[ -n "$pattern" ]]; then
        if [[ "$pattern" =~ ^[0-9]+$ ]]; then
            # Job ID - exact match
            debug_log "Using job ID search for: $pattern"
            results=$(squeue -u "$TARGET_USER" | grep -E "(JOBID|$pattern)")
        else
            # Job name pattern - try progressive matching
            debug_log "Using job name search for: $pattern"
            
            # Try exact pattern first
            results=$(squeue -u "$TARGET_USER" | grep -E "(JOBID|$pattern)")
            
            # If no results and pattern is long, try progressively shorter patterns
            if [[ $(echo "$results" | wc -l) -le 1 && ${#pattern} -gt 8 ]]; then
                debug_log "Exact pattern failed, trying shorter patterns"
                
                # Try truncated versions (common SLURM truncation points)
                for len in 8 6 4; do
                    if [[ ${#pattern} -gt $len ]]; then
                        short_pattern="${pattern:0:$len}"
                        debug_log "Trying shortened pattern: '$short_pattern'"
                        results=$(squeue -u "$TARGET_USER" | grep -E "(JOBID|$short_pattern)")
                        if [[ $(echo "$results" | wc -l) -gt 1 ]]; then
                            debug_log "Found matches with shortened pattern: '$short_pattern'"
                            break
                        fi
                    fi
                done
            fi
        fi
    else
        # All jobs for user
        results=$(squeue -u "$TARGET_USER")
    fi
    
    echo "$results"
}

# Enhanced function to check job history using sacct
check_job_history() {
    local pattern="$1"
    
    debug_log "Checking job history for pattern: '$pattern'"
    
    if [[ -n "$pattern" ]]; then
        if [[ "$pattern" =~ ^[0-9]+$ ]]; then
            # Job ID - check specific job
            debug_log "Checking sacct for job ID: $pattern"
            sacct -j "$pattern" --format=JobID,JobName,State,ExitCode,Start,End,Elapsed --parsable2 2>/dev/null
        else
            # Job name pattern - check recent jobs
            debug_log "Checking sacct for job name pattern: $pattern"
            # Get recent jobs (last 24 hours) and filter by pattern
            sacct -u "$TARGET_USER" --starttime=$(date -d '1 day ago' +%Y-%m-%d) \
                  --format=JobID,JobName,State,ExitCode,Start,End,Elapsed --parsable2 2>/dev/null | \
                  grep -i "$pattern"
        fi
    else
        # Recent jobs for user
        sacct -u "$TARGET_USER" --starttime=$(date -d '1 day ago' +%Y-%m-%d) \
              --format=JobID,JobName,State,ExitCode,Start,End,Elapsed --parsable2 2>/dev/null | head -10
    fi
}

# Function to parse sacct output and show user-friendly status
show_job_history_status() {
    local history_output="$1"
    local pattern="$2"
    
    if [[ -z "$history_output" ]]; then
        return 1
    fi
    
    echo "Recent Job History:"
    echo "=================="
    
    # Parse sacct output (skip header)
    echo "$history_output" | tail -n +2 | while IFS='|' read -r jobid jobname state exitcode start end elapsed; do
        # Skip empty lines and sub-jobs (those with dots)
        if [[ -n "$jobid" && ! "$jobid" =~ \. ]]; then
            # Color code based on state
            case "$state" in
                "COMPLETED")
                    if [[ "$exitcode" == "0:0" ]]; then
                        status_icon="✅"
                        status_color="\033[32m"  # Green
                    else
                        status_icon="⚠️"
                        status_color="\033[33m"  # Yellow
                    fi
                    ;;
                "FAILED"|"CANCELLED"|"TIMEOUT")
                    status_icon="❌"
                    status_color="\033[31m"  # Red
                    ;;
                "RUNNING")
                    status_icon="🔄"
                    status_color="\033[34m"  # Blue
                    ;;
                *)
                    status_icon="❓"
                    status_color="\033[37m"  # White
                    ;;
            esac
            
            printf "%s %sJob %s (%s): %s%s - Exit: %s - Runtime: %s\033[0m\n" \
                   "$status_icon" "$status_color" "$jobid" "$jobname" "$state" "\033[0m" "$exitcode" "$elapsed"
            
            # If this job completed, show end time
            if [[ "$state" == "COMPLETED" || "$state" == "FAILED" ]]; then
                echo "   Finished: $end"
            fi
        fi
    done
    
    return 0
}

# Enhanced function to find output files with better pattern matching
find_output_files_enhanced() {
    local pattern="$1"
    
    debug_log "Looking for output files with pattern: '$pattern'"
    
    if [[ -n "$pattern" ]]; then
        if [[ "$pattern" =~ ^[0-9]+$ ]]; then
            # Job ID - look for files ending with that ID
            debug_log "Searching for output files with job ID: $pattern"
            find . -maxdepth 1 -name "*${pattern}.*" -type f \( -name "*.out" -o -name "*.err" -o -name "*.log" \) 2>/dev/null | head -10
        else
            # Pattern match - try multiple variations
            debug_log "Searching for output files with name pattern: $pattern"
            {
                # Try exact pattern
                find . -maxdepth 1 -name "${pattern}*" -type f \( -name "*.out" -o -name "*.err" -o -name "*.log" \) 2>/dev/null
                # Try shortened patterns if exact fails
                if [[ ${#pattern} -gt 8 ]]; then
                    for len in 8 6 4; do
                        if [[ ${#pattern} -gt $len ]]; then
                            short_pattern="${pattern:0:$len}"
                            find . -maxdepth 1 -name "${short_pattern}*" -type f \( -name "*.out" -o -name "*.err" -o -name "*.log" \) 2>/dev/null
                        fi
                    done
                fi
            } | sort -u | head -10
        fi
    else
        # All recent job output files
        find . -maxdepth 1 -type f \( -name "*.out" -o -name "*.err" -o -name "*.log" \) -newer /tmp/last_hour 2>/dev/null || \
        ls -t *.{out,err,log} 2>/dev/null | head -10
    fi
}

# Function to get best output file for monitoring
get_output_file_enhanced() {
    local pattern="$1"
    local output_files
    
    output_files=$(find_output_files_enhanced "$pattern")
    
    if [[ -n "$output_files" ]]; then
        # Prefer .out files, then .log files
        echo "$output_files" | grep "\.out$" | head -1 || \
        echo "$output_files" | grep "\.log$" | head -1 || \
        echo "$output_files" | head -1
    fi
}

# Function to provide helpful suggestions when searches fail
provide_search_suggestions() {
    local pattern="$1"
    
    echo ""
    echo "🔍 Search Tips:"
    echo "=============="
    
    if [[ -n "$pattern" ]]; then
        echo "Pattern '$pattern' not found. Try:"
        
        # Suggest shorter patterns
        if [[ ${#pattern} -gt 4 ]]; then
            echo "  jm ${pattern:0:8}     # Shorter pattern (SLURM truncates job names)"
            echo "  jm ${pattern:0:4}     # Even shorter pattern"
        fi
        
        # Suggest looking at recent jobs
        echo "  jm                 # Show all your jobs"
        echo "  squeue -u $TARGET_USER  # Manual job queue check"
        echo "  sacct -u $TARGET_USER --starttime=today  # Check completed jobs"
        
        # Check if it might be a typo by looking at similar job names
        echo ""
        echo "Recent job names that might match:"
        sacct -u "$TARGET_USER" --starttime=$(date -d '2 days ago' +%Y-%m-%d) --format=JobName --parsable2 2>/dev/null | \
        tail -n +2 | sort -u | grep -i "${pattern:0:4}" | head -5 | sed 's/^/  /'
    else
        echo "  jm pattern         # Monitor jobs matching 'pattern'"
        echo "  jm 41005547        # Monitor specific job ID"
        echo "  jm -d pattern      # Debug mode for troubleshooting"
    fi
}

# Header
if [[ "$QUIET_MODE" != true ]]; then
    echo "=========================================="
    echo "Enhanced Universal Job Monitor v2.0"
    echo "Target: ${JOB_PATTERN:-'all jobs'} (user: $TARGET_USER)"
    echo "Refresh: ${REFRESH_INTERVAL}s | Press Ctrl+C to exit"
    echo "=========================================="
fi

# Enhanced Phase 1: Wait for job to start, with better completion detection
phase1_monitor_enhanced() {
    local consecutive_empty=0
    local max_empty=2  # Reduced from 3 for faster completion detection
    local check_history_after=1  # Check history after first empty result
    
    while true; do
        if [[ "$QUIET_MODE" != true ]]; then
            clear
            echo "=========================================="
            echo "Job Monitor - Waiting Phase"
            echo "Time: $(date)"
            echo "=========================================="
        fi
        
        # Show job status with enhanced matching
        local jobs_output
        jobs_output=$(find_matching_jobs_enhanced "$JOB_PATTERN")
        
        if [[ -n "$jobs_output" && $(echo "$jobs_output" | wc -l) -gt 1 ]]; then
            if [[ "$QUIET_MODE" != true ]]; then
                echo "Job Queue Status:"
                echo "$jobs_output"
            fi
            consecutive_empty=0
        else
            consecutive_empty=$((consecutive_empty + 1))
            if [[ "$QUIET_MODE" != true ]]; then
                echo "No active jobs found in queue"
            fi
            
            # Check job history early if we have a pattern
            if [[ $consecutive_empty -ge $check_history_after && -n "$JOB_PATTERN" ]]; then
                debug_log "Checking job history due to empty queue"
                local history_output
                history_output=$(check_job_history "$JOB_PATTERN")
                
                if [[ -n "$history_output" ]]; then
                    if [[ "$QUIET_MODE" != true ]]; then
                        echo ""
                        if show_job_history_status "$history_output" "$JOB_PATTERN"; then
                            echo ""
                            echo "💡 Jobs may have completed quickly - checking for output files..."
                        fi
                    fi
                fi
            fi
        fi
        
        if [[ "$QUIET_MODE" != true ]]; then
            echo ""
            echo "Output Files:"
        fi
        
        # Check for output files with enhanced matching
        local output_files
        output_files=$(find_output_files_enhanced "$JOB_PATTERN")
        
        if [[ -n "$output_files" ]]; then
            if [[ "$QUIET_MODE" != true ]]; then
                echo "$output_files"
            fi
            
            # Check if we have a running job with content
            local running_job
            running_job=$(echo "$jobs_output" | grep " R ")
            local out_file
            out_file=$(get_output_file_enhanced "$JOB_PATTERN")
            
            if [[ -n "$running_job" && -s "$out_file" ]]; then
                if [[ "$QUIET_MODE" != true ]]; then
                    echo ""
                    echo "✅ Job is running and producing output!"
                    echo "Switching to live progress view in 3 seconds..."
                    sleep 3
                fi
                return 0  # Success - move to phase 2
            elif [[ -s "$out_file" ]]; then
                # Output file exists but no running job - likely completed
                if [[ "$QUIET_MODE" != true ]]; then
                    echo ""
                    echo "📄 Output file found but job not running - likely completed"
                    echo "Showing final output..."
                    sleep 2
                fi
                return 0  # Move to phase 2 to show output
            fi
        else
            if [[ "$QUIET_MODE" != true ]]; then
                echo "No output files found yet"
            fi
        fi
        
        # Check if no jobs have been found for a while
        if [[ $consecutive_empty -ge $max_empty ]]; then
            if [[ -n "$output_files" ]]; then
                if [[ "$QUIET_MODE" != true ]]; then
                    echo ""
                    echo "⚠️  No active jobs found, but output files exist"
                    echo "Job may have completed - showing output"
                fi
                return 0
            else
                echo ""
                echo "❌ No matching jobs or output files found"
                
                # Show job history one more time for context
                if [[ -n "$JOB_PATTERN" ]]; then
                    local history_output
                    history_output=$(check_job_history "$JOB_PATTERN")
                    if [[ -n "$history_output" ]]; then
                        echo ""
                        show_job_history_status "$history_output" "$JOB_PATTERN"
                    fi
                fi
                
                provide_search_suggestions "$JOB_PATTERN"
                return 1
            fi
        fi
        
        sleep "$REFRESH_INTERVAL"
    done
}

# Enhanced Phase 2: Show live progress with better completion detection
phase2_monitor_enhanced() {
    local out_file
    out_file=$(get_output_file_enhanced "$JOB_PATTERN")
    
    if [[ ! -f "$out_file" ]]; then
        echo "❌ Output file not found"
        return 1
    fi
    
    local err_file="${out_file%.out}.err"
    [[ "$out_file" == *.log ]] && err_file="${out_file%.log}.err"
    
    if [[ "$QUIET_MODE" != true ]]; then
        echo ""
        echo "=========================================="
        echo "Live Progress Monitor"
        echo "=========================================="
        echo "Following: $out_file"
        echo "Error file: $err_file"
        echo ""
    fi
    
    # Check if job is already completed before starting tail
    local initial_check
    initial_check=$(find_matching_jobs_enhanced "$JOB_PATTERN")
    if [[ -z "$initial_check" || $(echo "$initial_check" | wc -l) -le 1 ]]; then
        # No running job - check why it ended
        local final_status
        final_status=$(check_job_history "$JOB_PATTERN")
        
        # Determine completion reason
        local completion_reason="COMPLETED"
        local completion_icon="🎯"
        local completion_message="Job appears to be completed"
        
        if [[ -n "$final_status" ]]; then
            local latest_job_state
            latest_job_state=$(echo "$final_status" | tail -n +2 | head -1 | cut -d'|' -f3)
            
            case "$latest_job_state" in
                "CANCELLED")
                    completion_reason="CANCELLED"
                    completion_icon="🛑"
                    completion_message="Job was cancelled"
                    ;;
                "FAILED")
                    completion_reason="FAILED"
                    completion_icon="❌"
                    completion_message="Job failed"
                    ;;
                "TIMEOUT")
                    completion_reason="TIMEOUT"
                    completion_icon="⏰"
                    completion_message="Job timed out"
                    ;;
            esac
        fi
        
        if [[ "$QUIET_MODE" != true ]]; then
            echo "$completion_icon $completion_message - showing final output:"
            echo "======================================================"
        fi
        
        # Show the last part of the output file
        if [[ -s "$out_file" ]]; then
            tail -50 "$out_file"
        else
            echo "Output file is empty"
        fi
        
        # Check for errors
        if [[ -f "$err_file" && -s "$err_file" ]]; then
            echo ""
            echo "⚠️  Error file contents:"
            echo "======================="
            tail -20 "$err_file"
        fi
        
        # Show final job status from history
        local history_output
        history_output=$(check_job_history "$JOB_PATTERN")
        if [[ -n "$history_output" ]]; then
            echo ""
            show_job_history_status "$history_output" "$JOB_PATTERN"
        fi
        
        return 0
    fi
    
    # Start tailing the file for live monitoring
    tail -f "$out_file" &
    local tail_pid=$!
    
    # Background job status checker with enhanced completion detection
    while true; do
        sleep 30  # Check every 30 seconds
        
        # Check if job is still running
        local still_running
        still_running=$(find_matching_jobs_enhanced "$JOB_PATTERN")
        
        if [[ -z "$still_running" || $(echo "$still_running" | wc -l) -le 1 ]]; then
            # Job no longer in queue - check why it ended
            local final_status
            final_status=$(check_job_history "$JOB_PATTERN")
            
            # Determine job completion reason
            local completion_reason="COMPLETED"
            local completion_icon="🎯"
            local completion_message="JOB COMPLETED"
            
            if [[ -n "$final_status" ]]; then
                # Parse the most recent job status
                local latest_job_state
                latest_job_state=$(echo "$final_status" | tail -n +2 | head -1 | cut -d'|' -f3)
                
                case "$latest_job_state" in
                    "CANCELLED")
                        completion_reason="CANCELLED"
                        completion_icon="🛑"
                        completion_message="JOB CANCELLED"
                        ;;
                    "FAILED")
                        completion_reason="FAILED"
                        completion_icon="❌"
                        completion_message="JOB FAILED"
                        ;;
                    "TIMEOUT")
                        completion_reason="TIMEOUT"
                        completion_icon="⏰"
                        completion_message="JOB TIMED OUT"
                        ;;
                    "COMPLETED")
                        completion_reason="COMPLETED"
                        completion_icon="🎯"
                        completion_message="JOB COMPLETED"
                        ;;
                    *)
                        completion_reason="ENDED"
                        completion_icon="🔚"
                        completion_message="JOB ENDED"
                        ;;
                esac
            fi
            
            if [[ "$QUIET_MODE" != true ]]; then
                echo ""
                echo "=========================================="
                echo "$completion_icon $completion_message at $(date)"
                echo "=========================================="
                
                # Show specific message based on completion reason
                case "$completion_reason" in
                    "CANCELLED")
                        echo "💡 This job was cancelled (likely via 'scancel' command)"
                        echo "   If this was intentional, no further action needed"
                        echo "   If accidental, you may want to resubmit the job"
                        ;;
                    "FAILED")
                        echo "💡 Job failed during execution - check error logs below"
                        ;;
                    "TIMEOUT")
                        echo "💡 Job exceeded time limit - consider requesting more time"
                        ;;
                    "COMPLETED")
                        echo "💡 Job completed successfully"
                        ;;
                esac
                
                echo ""
                
                # Show detailed job history
                if [[ -n "$final_status" ]]; then
                    show_job_history_status "$final_status" "$JOB_PATTERN"
                fi
                
                # Show final file sizes and handle different completion types
                if [[ -f "$out_file" ]]; then
                    local out_size
                    out_size=$(stat -f%z "$out_file" 2>/dev/null || stat -c%s "$out_file" 2>/dev/null || echo "unknown")
                    echo "Output size: $out_size bytes"
                fi
                
                if [[ -f "$err_file" ]]; then
                    local err_size
                    err_size=$(stat -f%z "$err_file" 2>/dev/null || stat -c%s "$err_file" 2>/dev/null || echo "0")
                    echo "Error size: $err_size bytes"
                    
                    # For cancelled jobs, show if there were any errors before cancellation
                    if [[ "$err_size" != "0" && "$err_size" != "unknown" ]] && [[ $err_size -gt 0 ]]; then
                        if [[ "$completion_reason" == "CANCELLED" ]]; then
                            echo ""
                            echo "⚠️  Error messages before cancellation (last 10 lines):"
                        else
                            echo ""
                            echo "⚠️  Error file contents (last 10 lines):"
                        fi
                        tail -10 "$err_file" 2>/dev/null
                    elif [[ "$completion_reason" == "CANCELLED" ]]; then
                        echo "✅ No errors logged before cancellation"
                    fi
                fi
                
                # Special handling for cancelled jobs
                if [[ "$completion_reason" == "CANCELLED" ]]; then
                    echo ""
                    echo "🔧 Cancellation Notes:"
                    echo "====================="
                    echo "• Job was terminated via 'scancel' or SLURM management"
                    echo "• Any partial output files remain available"
                    echo "• To resubmit: check your job script and run 'sbatch' again"
                    echo "• To cleanup: consider removing partial output files"
                fi
            fi
            break
        else
            local running_jobs
            running_jobs=$(echo "$still_running" | grep " R " | wc -l)
            if [[ "$QUIET_MODE" != true && $running_jobs -gt 0 ]]; then
                echo ""
                echo "--- Status check at $(date) - $running_jobs job(s) still running ---"
                echo "$still_running" | grep " R "
                echo "--- Continuing output monitoring ---"
            fi
        fi
    done
    
    # Cleanup
    kill $tail_pid 2>/dev/null
    
    if [[ "$QUIET_MODE" != true ]]; then
        echo ""
        echo "Monitoring complete. Final output files:"
        find_output_files_enhanced "$JOB_PATTERN"
    fi
}

# Main execution with enhanced error handling
main() {
    debug_log "Starting enhanced job monitor with pattern: '$JOB_PATTERN'"
    
    if phase1_monitor_enhanced; then
        phase2_monitor_enhanced
    else
        debug_log "Phase 1 failed, exiting"
        exit 1
    fi
}

# Run main function
main