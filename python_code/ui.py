
from peer import Peer

peer = Peer()


print("Welcome to chat program, type !exit to exit, !clients to see clients, !name to change your name")

peer.start_threads()
# User Loop
while True:
    # Get the message from the user
    message = input("")
    if message.startswith('!exit'):
        print("Exiting")
        break
    elif message.startswith('!clients'):
        print(peer.get_clients())
        continue
    elif message.startswith("!name"):
        peer.change_nickname(message.split(" ")[1])
        print(f"Your name changed to {peer.nickname}")
        continue
    peer.send_message(message)

peer.stop_threads()
peer.close()