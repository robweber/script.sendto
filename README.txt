SendTo

About:

Many households now have XBMC running on multiple devices in the home. Pieces like MySQL functionality and path substitution are good ways to make sure your music and video files are available and synchronized by any XBMC host available. A function that was always missing for me though was a real awareness of what was happening between each host instance. Consider the following scenerios: 

Scenerio 1
You're in room A of the house listening to music on XBMC. You decide that you'd like to continue listening while eating a meal in room B. Even with MySQL setup within your home you'd have to stop the music, go to the next XBMC host, find the song, and resume. If the file you are playing is actually part of a larger playlist you'd have to save the playlist or recreate it on the other XBMC machine, making the process even more complicated.

Scenerio 2
You're watching a TV show on your main HTPC. Your children or significant other ask that they use the larger TV. Luckily you have a iPad running XBMC; however you'll still have to stop what you're doing, find the TV show on your iPad and then continue watching. 

The SendTo addon seeks to make these processes easier by providing some automation between hosts. 

How Does It Work:

In the Programs area of XBMC you can launch the SendTo addon and define each of your hosts. I really wanted to use only native XBMC windows so adding hosts will bring up multiple prompts to collect information. Once a host is added you can click on it to see what is currently playing and perform the following actions: 

Transfer now playing - essentially this is a "pull" of the current playlist from a remote host to the current one. This will stop all media playing on the remote host and play the file where it left off on the new device. 

Start playing this file - Starts playing the selected file from the beginning 
Copy playlist, starting here - Copies the entire playlist from the remote machine but starts playback on the file you've specified
Stop playback - stops playing media on the remote host
Send Notification - type a message to send to the remote host

Sending Media:

With proper skin support (important!) you can launch the SendTo addon while watching a video or playing music on XBMC. The addon will ask you which XBMC host you wish to send your video or music playlist to, and then run the necessary commands via the JSONRPC interface to recreate the playlist and continue the file exactly where you left off on the first XBMC instance. The "Send" and "Transfer" commands are essentially mirrors of each other except one pushes media to a remote host and the other pulls media from one. 

How Can I Use It:

Once the addon is installed and the hosts added a few other pieces must exist in order to send files between the hosts. 

a) Enable Web Services (JSONRPC) under the Services section of XBMC on all hosts
b) Make sure each XBMC host has the same sources defined so they can play the sent files
c) Proper skin support. The addon can easily be added to the Music and Video menus by adding an option to call XBMC.RunScript(script.sendto,mode=1000). An alternative to this would be to map the RunScript command to a button on your remote. 

Disclaimer:

This is not airplay-like functionality! This addon is not streaming via upnp or any other protocol from Host A to Host B. We are stopping file playback, and then resuming it on another device so both must have access to the original source. MySQL and path subsititution are not necessary; however access to the sources on both machines is. MySQL is just a nice bonus if you want the watched flags and other info to line up when continuing playback from device to device. 
