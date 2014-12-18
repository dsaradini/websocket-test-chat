var WSClient = function() {
	this.ws = null;
	this.call_map = {};
};

WSClient.prototype.register = function(cmd, callback) {
	this.call_map[cmd] = callback;
};


WSClient.prototype._dispatch = function(msg) {
	var fn = this.call_map[msg.cmd] || function(x) {
		console.log("Unknown message: "+msg.cmd)
	};
	setTimeout(function() {
		fn(msg.data);
	},100);
};

WSClient.prototype.connect = function(ws_url) {
	var self = this;

	if (this.ws) {
		this.close()
	}
	this.closing = false;
	this.ws = new WebSocket(ws_url);
	this.ws.onmessage = function(msg_event) {
		var json_data = JSON.parse(msg_event.data);
		self._dispatch(json_data);
	};
	this.ws.onclose = function(msg_close) {
		self.ws = null;
		if (!self.closing) {
			setTimeout(function() {
				self.connect(ws_url)
			}, 2000);
		}
	}
};

WSClient.prototype.send = function(text) {
	if (this.ws) {
		var data = JSON.stringify({
			cmd: "ch.exodoc.send_message",
			data: text
		});
		this.ws.send(data);
	} else {
		// pending queue NYI
	}
};

WSClient.prototype.close = function() {
	this.closing = true;
	this.ws.close();
};