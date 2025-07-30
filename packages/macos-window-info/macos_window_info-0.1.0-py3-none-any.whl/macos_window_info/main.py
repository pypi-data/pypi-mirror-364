import time
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListExcludeDesktopElements, kCGNullWindowID
from Foundation import NSSet, NSMutableSet


def main():
    """Main function to monitor window movements."""
    print('Monitoring window movements. Press Ctrl+C to exit.')
    prev_windows = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID)

    try:
        while True:
            time.sleep(1)
            curr_windows = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID)
            prev_set = NSMutableSet.setWithArray_(prev_windows)
            curr_set = NSSet.setWithArray_(curr_windows)
            moved = NSMutableSet.setWithArray_(prev_windows)
            moved.minusSet_(curr_set)
            if len(moved) > 0:
                for win in moved:
                    pid = win.get('kCGWindowOwnerPID', 'N/A')
                    title = win.get('kCGWindowName', 'N/A')
                    exe = win.get('kCGWindowOwnerName', 'N/A')
                    print(f"PID: {pid}, Executable: {exe}, Title: {title}")
            prev_windows = curr_windows
    except KeyboardInterrupt:
        print('Stopped monitoring.')


if __name__ == "__main__":
    main()
