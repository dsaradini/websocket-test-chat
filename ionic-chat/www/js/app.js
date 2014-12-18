// Ionic Starter App

// angular.module is a global place for creating, registering and retrieving Angular modules
// 'starter' is the name of this angular module example (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
chatApp = angular.module('starter', ['ionic']);

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

chatApp.controller('MessageListCtrl', ['$scope', '$ionicScrollDelegate',
  	function($scope, $ionicScrollDelegate) {
		$scope.ws = null;
		$scope.comments = [];
		$scope.comment_text = "";

		$scope.init = function(ws_url) {
			$scope.client = new WSClient();
			console.log($ionicScrollDelegate.$getByHandle('listScroll').getScrollPosition());
			$scope.client.register("ch.exodoc.new_message", function(data) {
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
				console.log($ionicScrollDelegate.$getByHandle('listScroll'));
				console.log($ionicScrollDelegate.$getByHandle('listScroll').getScrollPosition());
				$ionicScrollDelegate.$getByHandle('listScroll').scrollBottom();
			});
			$scope.client.register("ch.exodoc.join", function(data) {
				$scope.$apply(function() {
					$scope.comments.push({
						system: true,
						text: "User '"+data.user+"' joined the chat... Welcome!"
					});
				});
			});
			$scope.client.register("ch.exodoc.leave", function(data) {
				$scope.$apply(function() {
					$scope.comments.push({
						system: true,
						text: "User '"+data.user+"' leaved the chat... Goodbye."
					});
				});
			});
			$scope.client.connect(ws_url || WS_URL);
		};
		$scope.submit = function() {
			if ($scope.client) {
				$scope.client.send($scope.comment_text);
			}
			$scope.comment_text = "";
		}
	}]);

chatApp.run(function($ionicPlatform) {
  $ionicPlatform.ready(function() {
    // Hide the accessory bar by default (remove this to show the accessory bar above the keyboard
    // for form inputs)
    if(window.cordova && window.cordova.plugins.Keyboard) {
      cordova.plugins.Keyboard.hideKeyboardAccessoryBar(true);
    }
    if(window.StatusBar) {
      StatusBar.styleDefault();
    }
  });
})
