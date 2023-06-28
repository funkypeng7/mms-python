import sys
import json

def main() -> None:
    while(True):
        # Receive a message from the C# application on the
        # Stdin stream and store it inside a variable.
        received = input()

        object = json.loads(received)
        
        respondBody = {
            "actions" : [
                {
                    "actionType" : 0,
                    "jsonBody" : json.dumps({
                        "left" : 0,
                        "right" : 0,
                    })
                }
            ]
        }
        # Send the message received from the C# application
        # back to the C# application through the Stdout stream
        sys.stdout.write(json.dumps(respondBody) + '\n')


main()