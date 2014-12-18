var chatApp = angular.module('chatApp', [

]);

chatApp.config(['$interpolateProvider', '$httpProvider',
	function ($interpolateProvider, $httpProvider) {
		$interpolateProvider.startSymbol('{&');
  		$interpolateProvider.endSymbol('&}');
		$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    	$httpProvider.defaults.xsrfCookieName = 'csrftoken';
	}]);


chatApp.directive('ngEnter', function() {
        return function(scope, element, attrs) {
            element.bind("keydown keypress", function(event) {
                if(event.which === 13 && !event.shiftKey) {
					scope.$apply(function(){
							scope.$eval(attrs.ngEnter);
					});
					event.preventDefault();
                }
            });
        };
	});

chatApp.controller('MessageListCtrl', ['$scope',
  	function($scope) {
		$scope.ws = null;
		$scope.comments = [];
		$scope.comment_text = "";

		$scope.init = function(ws_url) {
			$scope.client = new WSClient();
			$scope.client.register("ch.exodoc.new_message", function(data) {
				var node = $(".chat-box")[0];
				// check if the scroll is at the bottom
				var shouldScrollBottom = node.scrollTop + node.offsetHeight === node.scrollHeight;
				$scope.$apply(function() {
					$scope.comments.push({
						system: false,
						author: data.user,
						text: data.text,
						date: new Date(data.date),
						self: data.self,
						img_url: 'http://www.gravatar.com/avatar/' + md5(data.user)+"?s=48&d=retro"
					});
				});
				setTimeout(function() {
					if (shouldScrollBottom) {
						node.scrollTop = node.scrollHeight;
					}
				}, 1);
			});
			$scope.client.register("ch.exodoc.join", function(data) {
				$scope.$apply(function() {
					$scope.comments.push({
						system: true,
						text: data.user+" joined the chat"
					});
				});
			});
			$scope.client.register("ch.exodoc.leave", function(data) {
				$scope.$apply(function() {
					$scope.comments.push({
						system: true,
						text: data.user+" leaved the chat"
					});
				});
			});
			$scope.client.connect(ws_url);
		};
		$scope.submit = function() {
			$scope.client.send($scope.comment_text);
			$scope.comment_text = "";

		}
	}]);
