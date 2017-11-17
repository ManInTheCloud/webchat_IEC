function onkey(event) {
            if (event.keyCode == 13) {
                msgsender();
            }
        }

		var thisuser=document.getElementById('thisuser').innerHTML;
		var thisroom=document.getElementById('thisroom').innerHTML;
		var userlist=new Array();
		var ws=null;
		function init(){
			if(ws!=null){
				closecon();
			}
			ws=new WebSocket('ws://localhost:8001');

			ws.onopen=function(){
				var username=thisuser;
				var date=new Date().toTimeString().substr(0,8);
				var message='join the room!';
				jdata={"message":message,"username":username,"date":date,"flag":3,"roomid":thisroom};
				sdata=JSON.stringify(jdata);
				ws.send(sdata);
				document.getElementById('status').innerHTML='Connection status: Online';
			}
			ws.onmessage=function(msg){
				var sdata=msg.data;
				var jdata=JSON.parse(sdata);
				var message=jdata['message'];
				var date=jdata['date'];
				var username=jdata['username'];
				if(jdata['flag']==3&&!has_user(username)){
					userlist.push(username);
				}
				if(jdata['flag']==4){
					userlist.pop(username);
				}
				updateOnlineList();
				msgToDisplay=document.createElement('p');
				msgToDisplay.innerHTML='('+date+')'+username+':'+message;
				document.getElementById('chatting').appendChild(msgToDisplay);
				var height = document.getElementById("chatting").scrollHeight;
				document.getElementById('chatting').scrollTop=height;
			}
			ws.onclose=function(){
				document.getElementById('status').innerHTML='Connection status: Offline';

			}
		}

		function closecon(){
			ws.close();
			userlist.length=0;
			updateOnlineList();
			}

		function msgsender(){
			var message=document.getElementById('msg').value;
			var username=thisuser
			var roomid=thisroom
			var date=new Date().toTimeString().substr(0,8);
			jdata={"roomid":roomid,"message":message,"username":username,"date":date,"flag":3};
			sdata=JSON.stringify(jdata);
			ws.send(sdata);
			document.getElementById('msg').value='';
		}

		window.onbeforeunload = function onbeforeunload_handler(){
			ws.close();
		}

		function updateOnlineList(){
			$("#onlinelist").empty();
			for(x in userlist){
				newUser=document.createElement('li');
				newUser.innerHTML=userlist[x];
				document.getElementById('onlinelist').appendChild(newUser);
			}
		}

		function has_user(username){
			for(x in userlist){
				if(userlist[x]==username){
				return 1;
				}
			}
			return 0;
		}
