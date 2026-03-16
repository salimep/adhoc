import os
import shutil
import pymqi
import time


# ===== MQ CONFIG =====
QMGR = b'TEST'
CHANNEL = b'NOAUTH.SVRCONN'
CONN_INFO = b'192.168.10.11(1414)'
QUEUE_NAME = b'FILE.IN.Q'

# ===== FILE CONFIG =====
BASE_DIR = '/root/ftp'
INPUT_DIR = os.path.join(BASE_DIR, 'input')
PROCESSED_DIR = os.path.join(BASE_DIR, 'processed')
ERROR_DIR = os.path.join(BASE_DIR, 'error')

current_time = time.time()
one_minute_ago = current_time - 60

def connect_mq():
    cd = pymqi.CD()
    cd.ChannelName = CHANNEL
    cd.ConnectionName = CONN_INFO
    cd.ChannelType = pymqi.CMQC.MQCHT_CLNTCONN
    cd.TransportType = pymqi.CMQC.MQXPT_TCP
    cd.MaxMsgLength = 99614720
    sco = pymqi.SCO()
    qmgr = pymqi.QueueManager(None)
    qmgr.connect_with_options(QMGR, cd=cd, sco=sco)

    return qmgr


def main():
    qmgr = connect_mq()
    queue = pymqi.Queue(qmgr)
    queue.open(QUEUE_NAME, pymqi.CMQC.MQOO_OUTPUT)

    try:
        if not os.listdir(INPUT_DIR):
            print("No files found in the input folder")
            exit(1)

        # Check Queue
        queue = pymqi.Queue(qmgr, QUEUE_NAME, pymqi.CMQC.MQOO_OUTPUT)
        for filename in os.listdir(INPUT_DIR):
            file_path = os.path.join(INPUT_DIR, filename)
            create_datetime = os.path.getatime(file_path)
            if create_datetime < one_minute_ago:
                    
                if not os.path.isfile(file_path):
                    exit(1)
                try:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                        #print (data)
    
                    queue.put(data)
                    print(f"✔ Sent: {filename}")
                    shutil.move(file_path, os.path.join(PROCESSED_DIR, filename))

                except pymqi.MQMIError as e:
                    print(f"✖ Error processing {filename}: {e}")
                    shutil.move(file_path, os.path.join(ERROR_DIR, filename))
            else:
                print ("file is latest : {}".format(create_datetime))

    finally:
        if queue.open:
            queue.close()
        qmgr.disconnect()


if __name__ == "__main__":
    main()
