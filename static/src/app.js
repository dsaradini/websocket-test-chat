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
				$scope.$apply(function() {
					$scope.comments.push({
						author: data.user,
						text: data.text
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