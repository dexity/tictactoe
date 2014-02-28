'use strict';

// App Module

var t3App = angular.module('t3App', [
    't3Controllers'
]);

var t3Controllers = angular.module('t3Controllers', []);
t3Controllers.controller('t3Ctrl', ['$scope', '$http', function($scope, $http){

    $scope.newGame = function(){
        $http.post("/new").success(function(data){
            window.location.href = "/" + data.game_id;
        });
    }
}]);