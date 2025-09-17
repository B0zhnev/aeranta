import subprocess
import sys


def main():
    worker_cmd = [sys.executable, '-m', 'celery', '-A', 'aeranta', 'worker', '-l', 'info']
    worker_proc = subprocess.Popen(worker_cmd)

    beat_cmd = [sys.executable, '-m', 'celery', '-A', 'aeranta', 'beat', '-l', 'info']
    beat_proc = subprocess.Popen(beat_cmd)

    try:
        worker_proc.wait()
        beat_proc.wait()
    except KeyboardInterrupt:
        print("Останавливаем Celery...")
        worker_proc.terminate()
        beat_proc.terminate()


if __name__ == "__main__":
    main()
