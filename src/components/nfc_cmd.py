import subprocess
from utils.event import AmpiEvent

def poll(ampi):
    process = subprocess.Popen(['nfc-poll'], 
                           stdout=subprocess.PIPE,
                           universal_newlines=True)

    while True:
        output = process.stdout.readline()
        for output in process.stdout.readlines():
            line = output.strip()
            if line.startswith("UID"):
                uid = line.split(":")[1].strip()
                if ampi is not None:
                    ampi.trigger_event(AmpiEvent.CARD_READ, uid)
                else:
                    print(uid)
        # Do something else
        return_code = process.poll()
        if return_code is not None:
            # print('RETURN CODE', return_code)
            # Process has finished, read rest of the output 
            
            break

if __name__ == '__main__':
    while True: 
        poll(None)