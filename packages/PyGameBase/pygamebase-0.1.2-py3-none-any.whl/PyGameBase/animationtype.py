import threading
import time
class TypeA:
    @staticmethod
    def on_slide(obj, attr, target, duration=1.0):
        def animate():
            start = getattr(obj, attr)
            steps = abs(target - start)
            if steps == 0:
                return
            step_time = duration / steps
            step = 1 if target > start else -1

            while getattr(obj, attr) != target:
                current = getattr(obj, attr)
                setattr(obj, attr, current + step)
                time.sleep(step_time)

        thread = threading.Thread(target=animate)
        thread.start()
    @staticmethod
    def on_zoom(obj, attr_scale, target, duration=1.0):
        def animate():
            start = getattr(obj, attr_scale)
            steps = 60
            step_time = duration / steps
            diff = target - start
            step = diff / steps

            current = start
            for _ in range(int(steps)):
                current += step
                
                setattr(obj, attr_scale, max(0.1, current))
                time.sleep(step_time)

            setattr(obj, attr_scale, max(0.1, target))

        thread = threading.Thread(target=animate)
        thread.start()
