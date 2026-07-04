import sys
import pyttsx3
import os

def main():
    if len(sys.argv) > 1:
        text = sys.argv[1]
        
        lock_file = os.path.join(os.environ.get('TEMP', '.'), 'antigravity_speaking.lock')
        try:
            with open(lock_file, "w") as f:
                f.write("1")
                
            # Initialize pyttsx3 engine
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)
            
            # Speak the text
            engine.say(text)
            engine.runAndWait()
        finally:
            if os.path.exists(lock_file):
                os.remove(lock_file)

if __name__ == "__main__":
    main()
