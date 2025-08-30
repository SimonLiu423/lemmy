#!/usr/bin/env python3
"""
Analyze codebase using Claude Code to create CLAUDE.md documentation.
This script processes directories in dependency order with parallel execution.
"""

import os
import sys
import argparse
import subprocess
import time
import signal
import threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from typing import Dict, List, Set, Optional


class DirectoryAnalyzer:
    """Analyzes codebase directories and generates CLAUDE.md documentation."""
    def __init__(self, folder_name: str, num_threads: int, delete_claude_md: bool, 
                 dry_run: bool, no_interactive: bool = False, no_reorganize: bool = False,
                 reorganize_only: bool = False):
        self.folder_name = folder_name
        self.num_threads = num_threads
        self.delete_claude_md = delete_claude_md
        self.dry_run = dry_run
        self.no_interactive = no_interactive
        self.no_reorganize = no_reorganize
        self.reorganize_only = reorganize_only
        self.logs_dir = f".claude-trace/{folder_name}"

        # Directory tracking
        self.directories: List[str] = []
        self.dir_to_index: Dict[str, int] = {}
        self.children: Dict[str, Set[str]] = defaultdict(set)
        self.parents: Dict[str, Optional[str]] = {}
        self.completed: Set[str] = set()
        self.processing: Set[str] = set()
        
        # Status tracking for display
        self.dir_status: Dict[str, str] = {}  # pending, processing, completed
        self.dir_thread: Dict[str, int] = {}  # Track which thread is processing
        
        # Thread synchronization for display updates
        self.display_lock = threading.Lock()
        self.last_display_time = 0
        self.min_display_interval = 0.1  # Minimum time between display updates

        # Setup signal handler
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, _signum, _frame):
        """Handle Ctrl-C gracefully"""
        print("\nCtrl-C detected. Exiting...")
        sys.exit(0)

    def setup_logs_directory(self):
        """Create logs directory"""
        if not self.dry_run:
            os.makedirs(self.logs_dir, exist_ok=True)
            print(f"Created logs directory: {self.logs_dir}")
        else:
            print(f"[DRY RUN] Would create logs directory: {self.logs_dir}")

    def delete_claude_files(self):
        """Delete all CLAUDE.md files if requested"""
        if not self.delete_claude_md:
            return

        claude_files = list(Path('.').rglob('CLAUDE.md'))

        if self.dry_run:
            print("[DRY RUN] Would delete the following CLAUDE.md files:")
            for file in claude_files:
                print(f"  - {file}")
        else:
            for file in claude_files:
                file.unlink()
            print(f"Deleted {len(claude_files)} CLAUDE.md files in the project")

    def get_all_directories(self) -> List[str]:
        """Get all directories using fd command"""
        try:
            result = subprocess.run(
                ['fd', '--type', 'd', '--hidden', '--exclude', '.git', '--exclude', '.claude'],
                capture_output=True,
                text=True,
                check=True
            )
            # Normalize paths by removing trailing slashes
            dirs = [d.rstrip('/') for d in result.stdout.strip().split('\n') if d]
            dirs.append('.')  # Add root directory
            return dirs
        except subprocess.CalledProcessError as e:
            print(f"Error running fd: {e}")
            sys.exit(1)

    def build_dependency_graph(self):
        """Build parent-child relationships"""
        self.directories = self.get_all_directories()

        # Build index mapping and initialize status
        for i, dir_path in enumerate(self.directories):
            self.dir_to_index[dir_path] = i
            self.dir_status[dir_path] = 'pending'

        # Build parent-child relationships
        for dir_path in self.directories:
            if dir_path == '.':
                self.parents[dir_path] = None
            else:
                parent = str(Path(dir_path).parent)
                self.parents[dir_path] = parent

                # Add to children set if parent exists in our list
                if parent in self.dir_to_index:
                    self.children[parent].add(dir_path)

    def get_leaf_directories(self) -> List[str]:
        """Get directories with no subdirectories"""
        return [d for d in self.directories if len(self.children[d]) == 0]
    
    def get_status_symbol(self, dir_path: str) -> str:
        """Get status symbol for directory"""
        status = self.dir_status.get(dir_path, 'pending')
        if status == 'pending':
            return '⏳'
        elif status == 'processing':
            thread = self.dir_thread.get(dir_path, '?')
            return f'🔄[T{thread}]'
        elif status == 'completed':
            return '✅'
        return '❓'
    
    def print_tree(self, dir_path: str = '.', prefix: str = '', is_last: bool = True):
        """Print directory tree with status"""
        # Get the display name
        if dir_path == '.':
            display_name = '.'
        else:
            display_name = os.path.basename(dir_path)
        
        # Print current directory with status
        connector = '└── ' if is_last else '├── '
        status = self.get_status_symbol(dir_path)
        print(f"{prefix}{connector}{display_name} {status}")
        
        # Get sorted children
        children_list = sorted(list(self.children.get(dir_path, [])))
        
        # Print children
        if children_list:
            extension = '    ' if is_last else '│   '
            for i, child in enumerate(children_list):
                is_last_child = (i == len(children_list) - 1)
                self.print_tree(child, prefix + extension, is_last_child)
    
    def update_and_print_tree(self, force: bool = False):
        """Clear screen and print updated tree"""
        with self.display_lock:
            # Throttle updates to reduce flicker
            current_time = time.time()
            if not force and (current_time - self.last_display_time) < self.min_display_interval:
                return
            self.last_display_time = current_time
            
            # Move cursor to top and clear screen (ANSI escape codes)
            print('\033[H\033[J', end='', flush=True)
            print("Directory Processing Status:")
            print("=" * 50)
            print("Legend: ⏳ Pending | 🔄[T#] Processing | ✅ Completed")
            print("=" * 50)
            self.print_tree()
            print("=" * 50, flush=True)

    def is_ready_to_process(self, dir_path: str) -> bool:
        """Check if a directory is ready to be processed"""
        if dir_path in self.completed or dir_path in self.processing:
            return False

        # Check if all children are completed
        children_dirs = self.children.get(dir_path, set())
        return all(child in self.completed for child in children_dirs)

    def process_directory(self, dir_path: str, thread_id: int, is_reorganize: bool = False):
        """Process a single directory"""
        # Update status to processing (with lock)
        with self.display_lock:
            self.dir_status[dir_path] = 'processing'
            self.dir_thread[dir_path] = thread_id
        self.update_and_print_tree()
        
        if self.dry_run:
            # Simulate processing with longer sleep
            time.sleep(0.5)
        else:
            # Sanitize directory name for log file
            if dir_path == '.':
                sanitized = 'root-reorganize' if is_reorganize else 'root'
            else:
                sanitized = dir_path.replace('/', '-').strip('-')

            # Choose the appropriate agent
            if is_reorganize:
                agent_command = '@agent-claude-md-hierarchy-organizer Reorganize the documentation structure of this project'
            else:
                agent_command = f'@agent-directory-documenter Document the directory: {dir_path}'

            # Execute claude-trace
            try:
                subprocess.run(
                    [
                        'claude-trace',
                        '--log', sanitized,
                        '--no-open',
                        '--run-with',
                        '-p', agent_command
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )

                # Move generated files to logs directory
                time.sleep(0.1)  # Avoid race conditions
                for ext in ['jsonl', 'html']:
                    src = f".claude-trace/{sanitized}.{ext}"
                    dst = f"{self.logs_dir}/{sanitized}.{ext}"
                    if os.path.exists(src):
                        os.rename(src, dst)

            except Exception as e:
                with self.display_lock:
                    print(f"\n[Thread {thread_id}] Error processing {dir_path}: {e}")
        
        # Update status to completed (with lock)
        with self.display_lock:
            self.dir_status[dir_path] = 'completed'
        self.update_and_print_tree()

    def print_configuration(self):
        """Print analysis configuration"""
        leaf_count = len(self.get_leaf_directories())

        print("=" * 50)
        print("Analysis configuration:")
        if self.dry_run:
            print("  MODE: DRY RUN (no actual processing)")
        print(f"  Threads: {self.num_threads}")
        print(f"  Log directory: {self.logs_dir}")
        print(f"  Total directories to analyze: {len(self.directories)}")
        print(f"  Leaf directories (no subdirectories): {leaf_count}")
        print("=" * 50)
        print()
        
        # Show initial tree
        print("Initial Directory Structure:")
        print("=" * 50)
        self.print_tree()
        print("=" * 50)
        print()
        if not self.no_interactive:
            input("Press Enter to start processing...")

    def run_parallel_processing(self):
        """Run dependency-aware parallel processing"""
        # Clear screen and show initial state
        self.update_and_print_tree()
        time.sleep(1)  # Brief pause to show initial state
        
        processed_count = 0
        thread_counter = 1

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = []

            while processed_count < len(self.directories):
                # Find directories ready to process
                ready_dirs = []
                for dir_path in self.directories:
                    if self.is_ready_to_process(dir_path):
                        ready_dirs.append(dir_path)
                        self.processing.add(dir_path)

                # Submit ready directories for processing
                for dir_path in ready_dirs:
                    thread_id = thread_counter
                    thread_counter = (thread_counter % self.num_threads) + 1

                    # Submit for processing (both dry run and real)
                    future = executor.submit(self.process_directory, dir_path, thread_id)
                    futures.append((future, dir_path))

                # Process completed futures
                if futures:
                    # Check for completed futures
                    completed_futures = []
                    for future, dir_path in futures:
                        if future.done():
                            completed_futures.append((future, dir_path))

                    for future, dir_path in completed_futures:
                        futures.remove((future, dir_path))
                        self.processing.remove(dir_path)
                        self.completed.add(dir_path)
                        processed_count += 1

                # Short sleep to avoid busy waiting
                if not ready_dirs:
                    time.sleep(0.1)

            # Wait for any remaining futures
            for future, dir_path in futures:
                future.result()
                self.processing.remove(dir_path)
                self.completed.add(dir_path)
                processed_count += 1

        # Final update to show all completed (force update)
        self.update_and_print_tree(force=True)
        
        print()
        print("=" * 50)
        if self.dry_run:
            print(f"[DRY RUN] All directories processed ({processed_count}/{len(self.directories)})")
            print("Analysis simulation complete! No actual processing was performed.")
        else:
            print(f"All directories processed ({processed_count}/{len(self.directories)})")
            print(f"Analysis complete! Logs are stored in: {self.logs_dir}/")
        print("=" * 50)
        
        # Run reorganization on root directory (unless disabled)
        if not self.no_reorganize:
            print()
            print("=" * 50)
            if self.dry_run:
                print("[DRY RUN] Would run documentation reorganization on root directory...")
                time.sleep(0.5)
                print("[DRY RUN] Documentation reorganization complete.")
            else:
                print("Running documentation reorganization on root directory...")
                self.process_directory('.', 1, is_reorganize=True)
                print("Documentation reorganization complete.")
            print("=" * 50)

    def run_reorganize_only(self):
        """Run only the documentation reorganization"""
        self.setup_logs_directory()
        
        print("=" * 50)
        print("Documentation Reorganization Mode")
        if self.dry_run:
            print("  MODE: DRY RUN (no actual processing)")
        print(f"  Log directory: {self.logs_dir}")
        print("=" * 50)
        print()
        
        if self.dry_run:
            print("[DRY RUN] Would run documentation reorganization on root directory...")
            time.sleep(0.5)
            print("[DRY RUN] Documentation reorganization complete.")
        else:
            print("Running documentation reorganization on root directory...")
            self.process_directory('.', 1, is_reorganize=True)
            print("Documentation reorganization complete.")
            print(f"Reorganization log: {self.logs_dir}/root-reorganize.{{jsonl,html}}")
        print("=" * 50)
    
    def run(self):
        """Main execution function"""
        # If reorganize-only mode, run that instead
        if self.reorganize_only:
            self.run_reorganize_only()
            return
            
        self.setup_logs_directory()
        self.delete_claude_files()
        self.build_dependency_graph()
        self.print_configuration()
        self.run_parallel_processing()


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Analyze codebase using Claude Code to create CLAUDE.md documentation'
    )
    parser.add_argument(
        '-f', '--folder',
        default=f"analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        help='Name of the folder to create under .claude-trace/ (default: analysis-TIMESTAMP)'
    )
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=4,
        help='Number of parallel threads (default: 4)'
    )
    parser.add_argument(
        '-d', '--delete',
        action='store_true',
        help='Delete all CLAUDE.md files in the project'
    )
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Dry run - show what would be executed without running'
    )
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Skip interactive prompts (useful for automation)'
    )
    parser.add_argument(
        '--no-reorganize',
        action='store_true',
        help='Skip documentation reorganization step'
    )
    parser.add_argument(
        '--reorganize-only',
        action='store_true',
        help='Only run documentation reorganization (skip documentation generation)'
    )

    args = parser.parse_args()
    
    # Validate conflicting options
    if args.reorganize_only and args.no_reorganize:
        print("Error: Cannot use --reorganize-only and --no-reorganize together")
        sys.exit(1)
    if args.reorganize_only and args.delete:
        print("Error: Cannot use --reorganize-only and --delete together")
        sys.exit(1)

    # Validate thread count
    if args.threads < 1:
        print("Error: Thread count must be a positive number")
        sys.exit(1)

    # Create and run analyzer
    analyzer = DirectoryAnalyzer(
        folder_name=args.folder,
        num_threads=args.threads,
        delete_claude_md=args.delete,
        dry_run=args.dry_run,
        no_interactive=args.no_interactive,
        no_reorganize=args.no_reorganize,
        reorganize_only=args.reorganize_only
    )
    analyzer.run()


if __name__ == '__main__':
    main()
