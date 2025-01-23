WebRTC Call
<details> <summary>Brief Overview of WebRTC</summary> <br/>
WebRTC is a technology that enables direct audio-video streaming between clients without the need for a server.
Modern browsers already have built-in WebRTC APIs.

RTCPeerConnection is the interface used to create WebRTC connections.
Each client needs to create an instance of this interface and initialize it properly:

javascript
Copy
Edit
const rtc_peer = new RTCPeerConnection({
    iceServers: [
        {
            urls: ['stun:stun1.l.google.com:19302', 'stun:stun3.l.google.com:19302']  // Allows clients to connect over the internet (see point 2)
        }
    ]
});
<br/> <details> <summary>1. Adding Media Tracks and Creating an RTCDataChannel</summary> <br/>
The addTrack(track) method allows you to add media tracks for transmission through the connection.
You can get the current webcam and microphone tracks and add them to the RTC connection:

javascript
Copy
Edit
const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
stream.getTracks().forEach(track => rtc_peer.addTrack(track));
On the receiving side, a callback ontrack(event) will be triggered for each added track:

javascript
Copy
Edit
const remote_stream = new MediaStream();
// remote_stream needs to be set somewhere for playback, e.g., an <audio> or <video> element.
// video_object.srcObject = remote_stream;

rtc_peer.ontrack = event => {
    remote_stream.addTrack(event.track);
}
In addition to media data, you can transmit arbitrary data through an RTC connection using an RTCDataChannel.

This can be useful for sending specific messages during a call:

To end the call;
To indicate that the participant has enabled/disabled their camera/microphone.
javascript
Copy
Edit
let datachannel = null;
One side uses the createDataChannel(str_channel_label) method:

javascript
Copy
Edit
datachannel = rtc_peer.createDataChannel('special_datachannel');
datachannel.onmessage = event => {
    // processDataChannel(JSON.parse(event.data));
}
The other side receives a callback ondatachannel(event):

javascript
Copy
Edit
rtc_peer.ondatachannel = event => {
    if (event.channel.label === 'special_datachannel') {
        datachannel = event.channel;
        datachannel.onmessage = event => {
            // processDataChannel(JSON.parse(event.data));
        }
    }
}
To send messages through the data channel, use the send(str) method:

javascript
Copy
Edit
datachannel.send(JSON.stringify({
    code: 'reject'
}));

datachannel.send(JSON.stringify({
    code: 'mute_microphone',
    value: true
}));
The sent messages will be received via the onmessage(event) callback.

</details> <details> <summary>2. Setting up `onicecandidate`</summary> <br/>
You need to set up the onicecandidate(event) callback, which will be triggered during step 3.

RTCIceCandidate represents a possible route through which the RTC connection can connect to a remote client.
This object contains the client's IP information, and there may be multiple candidates.
Some will have local IPs (192.168.1.*), while others will have external IPs (85.*.*.*).

STUN servers help to determine external IPs, which is why we configure them.

javascript
Copy
Edit
rtc_peer.onicecandidate = event => {
    const ice_route = event.candidate;
    
    // storing ice_route or sending it right now ...
};
Decide when to send ICE candidates: either directly inside the callback or after creating the offer/answer (step 3).

In this project, each candidate is sent immediately to the server, where they are stored in an array for each participant. After exchanging the offer/answer, all candidates are sent to the peer at once.

</details> <details> <summary>3. Creating an Offer and an Answer</summary> <br/>
Each participant must create a description of their transmitted data and exchange it with their peer.
This description forms the remote tracks.

RTCSessionDescription is the session description object. It consists of two fields:

javascript
Copy
Edit
{
    type: 'offer',  // or 'answer'
    sdp: '...'      // description of AV codecs, etc.
}
One participant creates an offer describing their stream using the createOffer(...) method and sends it to the peer:

javascript
Copy
Edit
const offer = await rtc_peer.createOffer({  // can be called without arguments
    offerToReceiveAudio: true,  // if the initiator transmits only audio, the answer will include only audio by default.
    offerToReceiveVideo: true   // with these options, both video and audio will be included if available.
});
await rtc_peer.setLocalDescription(offer);

// sending offer ...
The other participant creates an answer using createAnswer() and sends it to the initiator:

javascript
Copy
Edit
await rtc_peer.setRemoteDescription(offer_from_initiator);

const answer = await rtc_peer.createAnswer();
await rtc_peer.setLocalDescription(answer);

// sending answer ...
javascript
Copy
Edit
// initiator
await rtc_peer.setRemoteDescription(answer_from_subscriber);
</details> <details> <summary>4. Adding ICE Candidates</summary> <br/>
Finally, you need to add the received ICE candidates from your peer to the RTC connection:

javascript
Copy
Edit
// receiving ice_routes_from_subscriber ...

ice_routes_from_subscriber.forEach(route => rtc_peer.addIceCandidate(route));
And voilà, it works!

</details> <br/>
To summarize, for audio-video streaming via WebRTC, two clients need to exchange offers, answers, and ICE candidates. This establishes a direct connection without server involvement.
You just need to figure out how to perform this exchange.
That's what this project is for!

</details>
<br/>
Simple Call Between Two Participants via POST Requests:
Clients send their data to the server.
The server retransmits the data to the peer.
Clients establish a WebRTC connection, and the server forgets about the participants.
https://cmykcmyk.tw1.ru/call/

Running the Project
Install Django.

In webrtc_call/settings.py, edit ALLOWED_HOSTS to include your network address:

python
Copy
Edit
ALLOWED_HOSTS = ['127.0.0.1', '192.168.1.1']
In the terminal, run the following commands:
bash
Copy
Edit
python manage.py makemigrations
python manage.py makemigrations call
python manage.py migrate

python manage.py test
python manage.py runserver 0.0.0.0:8000
Open http://ip_addr:8000/call in your browser and ensure the site loads.
Your browser may block access to your media devices without HTTPS.
Add http://ip_addr:8000/ to your browser's exceptions:
https://stackoverflow.com/questions/40696280/unsafely-treat-insecure-origin-as-secure-flag-is-not-working-on-chrome
Open two tabs on your computer or access the site from your smartphone over home Wi-Fi.
Enjoy calling yourself!

