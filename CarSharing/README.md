# Requirements
- Car owners can use mobile client to register a car for rental. Backend server will process this request only if the car is available ( connection is possible) and is not already registered. (1 point)
- Users who want to rent a car cand use mobile client app to query the available cars from server, start the rental process and end the rental process. Backend server will process this request only if the car is available ( connection is possible) and car is not already rented. (1 point)
- During processing startRental or endRental requests, server will also send notification to car that rental process has started/ended. (1 point)
- Car should send a confirmation message that it processed the request successfully or an error message if it rental cannot be started/ended for various reasons. (1 point)

# Structure
## App.py
- Contains the simulated *client application*
- Works as a console application, where the main use-cases can be verified
### Supported commands:
- `register <car_ip:port>`
    - registers the given car in the *backend*
- `request_cars`
    - requests the list of registered (and rentable cars)
- `start_rental <car_ip:port>`
    - starts rental of the given car
- `end_rental <car_ip:port>`
    - starts rental of the given car
- `bad_message_type`
    - used to test the behaviour of the two actors (*client application* and *backend*) when the message type is not recongnized
### Usage
- in order to use this script, an user-id is given as a command-line parameter; Ex: `python App.py 3`
## Backend.py
- Contains the *backend* application
- Features an in-memory database
- Handles multiple client connections concurrently
## Car.py
- Contains code which simulates the behaviour of the car telematics unit

# Protocols
- The system contains two separate (mini) protocols: **Message** and **CarMessage**
## Message
- Used for the communication between the *application* and the *backend*
- multiple byte members come in big-endian order
### Format
- bytes 1 and 2: a client identifier
    - id `0` is reserved for the *backend*
- byte 3: message type
    - MSG_REGISTER = 0
    - MSG_POST_CAR = 1
    - MSG_REQUEST_CARS = 2
    - MSG_START_RENTAL = 3
    - MSG_END_RENTAL = 4
    - MSG_CAR_LIST = 5
    - ERR_SUCCESS = 6
    - ERR_BAD_FORMAT = 7
    - ERR_INVALID_TYPE = 8
    - ERR_ALREADY_REGISTERED = 9
    - ERR_NOT_REGISTERED = 10
    - ERR_ALREADY_RENTED = 11
    - ERR_NOT_RENTED = 12
    - ERR_CAR_UNAVAILABLE = 13
- bytes 4 and 5: payload size
- the rest of the message is the payload (must be < 2^16)
## CarMessage
- Used for the communication between the *backend* and the *car*
### Format
- byte 1: message type
    - MSG_START_RENTAL = 0
    - MSG_END_RENTAL = 1
    - MSG_PING = 2
    - ERR_SUCCESS = 3
    - ERR_FAIL = 4
- byte 2: reason code
    - REASON_NONE = 0
    - REASON_ALREADY_RENTED = 1
    - REASON_NOT_RENTED = 2
