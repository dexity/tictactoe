'use strict';

// App Module

var t3App = angular.module('t3App', [
    'btford.socket-io',
    't3Controllers'
])
.factory('socket', function (socketFactory) {
    return socketFactory({
        ioSocket: io.connect("/game")
    });
});

// Controllers

var t3Controllers = angular.module('t3Controllers', []);
t3Controllers.controller('t3Ctrl', ['$scope', 'socket', '$http', function($scope, socket, $http){
    $scope.userMark = 'O';
    $scope.serverMark = 'X';
    $scope.turn = 0;
    $scope.game_over = false;
    $scope.show_msg = false;
    $scope.message = false;

    $scope.rows = [
        [
            { id: 'c00', mark: '' },
            { id: 'c01', mark: '' },
            { id: 'c02', mark: '' }
        ],
        [
            { id: 'c10', mark: '' },
            { id: 'c11', mark: '' },
            { id: 'c12', mark: '' }
        ],
        [
            { id: 'c20', mark: '' },
            { id: 'c21', mark: '' },
            { id: 'c22', mark: '' }
        ]
    ];
    $scope.board = {};
    $scope.players = [
        {name: "User"},
        {name: "Server"}
    ];
    $scope.player = $scope.players[0];
    $scope.gameId = gameId;

    // Events
    socket.on("connect", function(){
        socket.emit("init", $scope.gameId);
    });

    socket.on("move:server", function(data){
        if (data.move){
            var row = data.move[0];
            var col = data.move[1];
            $scope.rows[row][col].mark = $scope.serverMark;
        }
        if (data.winner){
            $scope.game_over = true;
            $scope.message = $scope.winnerMsg(data.winner);
        }
        $scope.turn = 1;
    });

    socket.on("init", function(data){
        $scope.show_msg = true;
        $scope.board = data;
        for (var i = 0; i < 3; i++){
            for (var j = 0; j < 3; j++){
                $scope.rows[i][j].mark = data.rows[i][j].mark;
            }
        }
        if (data.winner){
            $scope.game_over = true;
            $scope.message = $scope.winnerMsg(data.winner);
        }
        if (data.next_turn === "server"){
            $scope.turn = 0;
        } else {
            $scope.turn = 1;
        }
    })

    $scope.newGame = function(){
        $http.post("/new").success(function(data){
            window.location.href = "/" + data.game_id;
        });
    }

    $scope.setPlayer = function(){
        if ($scope.gameStarted()){
            return; // Do nothing
        }
        if ($scope.player.name === "Server"){
            $scope.turn = 0;
            socket.emit("move:server", {gameId: $scope.gameId});
        }else {
            $scope.turn = 1;
        }
    }

    $scope.makeMove = function(cell){
        if (cell.mark === '' && $scope.turn === 1 && !$scope.game_over){
            $scope.turn = 0;
            var data = {
                move: cell2move(cell),
                gameId: $scope.gameId
            }
            socket.emit("move:user", data);
            cell.mark = $scope.userMark;
        }
    }

    $scope.gameStarted = function(){
        for (var i = 0; i < 3; i++){
            for (var j = 0; j < 3; j++){
                if ($scope.rows[i][j]["mark"] != ""){
                    return true;
                }
            }
        }
        return false;
    }

    $scope.winnerMsg = function(winner){
        if (!winner){
            return false;
        }
        var msg = {
            server: "You lost the game",
            user: "Congratulations. You won!",
            tie: "Tie indeed. Game over"
        }
        return msg[winner]
    }
}]);

var cell2move = function(cell){
    // Converts cell to move
    return [cell.id[1], cell.id[2]];
}


