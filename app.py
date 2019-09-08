import arcade
import os
from numpy import exp, array, random, dot
import numpy as np
import network as rnn

import utils as U
import genome as GE
Util   = U.oUtil()
Genome = GE.oGenome()

DEBUG = False
SPRITE_SCALING = 0.5
GRAVITY = 0
SCREEN_TITLE = "RNN + Genetic algorithm"

# GRIDE
ROW_COUNT = 30
COLUMN_COUNT = 30
WIDTH = 30
HEIGHT = 30
MARGIN = 0
SCREEN_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN

#ROBOTs
MOVEMENT_SPEED = 10
MAX = 200 if not DEBUG else 1
MAX_TIME = 10

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """
        Initializer
        """
        super().__init__(width, height, title)
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Sprite lists
        self.wall_list = None
        self.player_list = None
        self.score = 0
        self.score_timeout = 0
        self.generations = 0
        self.frame = 0

        # Set up the player
        self.player_sprite = None
        self.physics_engine = None

        # Create layer 1/2 (6 inputs, each with 6 neurons)
        self.layer1 = rnn.NeuronLayer(6, 6)
        self.layer2 = rnn.NeuronLayer(6, 4)
        self.perceptron = rnn.NeuralNetwork(self.layer1, self.layer2)
        self.genoma_list = []
        self.better = None

        #neuron
        self.better_count = 0
        self.neuron_action = [0, 0]
        self.index = 0
        self.lines_action = [0, 0, 0, 0]

        self.grid   = Util.grid 
        self.reward = Util.reward          

    def startnewgame(self):
        print('------------------startnewgame----------------') 
        self.generations += 1
        mutations = 0
        for x in range( MAX ):
            self.player_sprite = arcade.Sprite("images/ballon3.png",SPRITE_SCALING)
            self.player_sprite.center_x = 150 + random.uniform(1,50)
            self.player_sprite.center_y = 100
                                         # 6 imputs, 6 neuro, 4 saidas
            self.player_sprite.weights1 = 2 * random.random((6, 6)) - 1 if self.better == None else Util.copy(self.better.weights1)
            self.player_sprite.weights2 = 2 * random.random((6, 4)) - 1 if self.better == None else Util.copy(self.better.weights2) 
            self.player_sprite.reward   = 0
            self.player_sprite.index    = random.uniform(0, 1)
            self.player_sprite.physics  = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)                
            mutation1, mutation2, mutate = Genome.genome(self.player_sprite, self.better)
            if( mutate ):
                old = self.player_sprite.weights1
                self.player_sprite.weights1 = mutation1
                self.player_sprite.weights2 = mutation2
                mutations += 1            
                #diff befor / after mutation
                #print(np.setdiff1d(old, self.player_sprite.weights1))            

            self.player_list.append(self.player_sprite)           

        print('mutations',mutations)    

    def setup(self):

        self.score = 0
        self.score_timeout = 0

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()                   

        # Draw the grid
        for row in range(ROW_COUNT):
            for column in range(COLUMN_COUNT):
                x = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2
                y = (MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2
                # Draw the box
                if self.grid[row][column] == 1:
                    wall = arcade.Sprite("images/platform2.png", SPRITE_SCALING)
                    wall.center_x = x
                    wall.center_y = y
                    self.wall_list.append(wall)                        

        # Set up the player
        self.startnewgame()
        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.wall_list.draw()
        self.player_list.draw()

        # score
        arcade.draw_text(f"Time: {self.score}", 50, 630,arcade.csscolor.WHITE, 10)
        arcade.draw_text(f"Generations: {self.generations}", 50, 620,arcade.csscolor.WHITE, 10)        
 
        Genome.neuron(arcade, self.neuron_action[0], self.neuron_action[1], self.lines_action) 

        #if DEBUG :
        #    arcade.draw_text(f"right: {self.right} left: {self.left}", 50, 580,arcade.csscolor.WHITE, 10) 
        #    arcade.draw_text(f"top: {self.top} botton: {self.botton}", 50, 570,arcade.csscolor.WHITE, 10) 
                    
        #    arcade.draw_text(f"top-right:{self.grid[ self.top ][ self.right ]} botton-right:{self.grid[ self.botton ][ self.right ]}", 50, 500,arcade.csscolor.WHITE, 10) 
        #    arcade.draw_text(f"top-left: {self.grid[ self.top ][ self.left ]}  botton-left: {self.grid[ self.botton ][ self.left ]}", 50, 490,arcade.csscolor.WHITE, 10) 
       
        for player in self.player_list:                
            #arcade.draw_text(f"top",    player.position[0],    player.position[1]+25, arcade.csscolor.WHITE, 10) 
            #arcade.draw_text(f"botton", player.position[0],    player.position[1]-30, arcade.csscolor.WHITE, 10)
            #arcade.draw_text(f"right",  player.position[0]+20, player.position[1], arcade.csscolor.WHITE, 10) 
            #arcade.draw_text(f"left",   player.position[0]-25, player.position[1], arcade.csscolor.WHITE, 10)                
            arcade.draw_text(f"R: {player.reward*player.position[1]}", player.position[0],    player.position[1]+40 ,arcade.csscolor.WHITE, 10) 
           

    def update(self, delta_time):
        self.score_timeout += delta_time
        self.frame += delta_time
        self.score = int(self.score_timeout) % 60
        
        #if int(self.frame) % 30 : #1 p/ second 
        #    self.frame  = 0 
        for player in self.player_list :    
            player.physics.update() 
            
            top    = int(np.around( ( (player.position[1]+25) )/COLUMN_COUNT ))  # 25
            botton = int(np.around( ( (player.position[1]-30) )/COLUMN_COUNT ))  # 30
            right  = int(np.around( ( (player.position[0]+20) )/ROW_COUNT ))     # 20
            left   = int(np.around( ( (player.position[0]-25) )/ROW_COUNT ))     # 25
            if DEBUG :
                print( 'top',top, 'botton',botton, 'right',right, 'left',left)
            top    = top if top < 29 else 29
            right  = right if right < 29 else 29
            botton = botton if botton >= 0 else 0
            left   = left if left >= 0 else 0

            player.reward = self.reward[botton][left]

            line_top    = Util.check_wall_top( self.grid, top, left )
            line_botton = Util.check_wall_botton( self.grid, botton, left )
            line_left   = Util.check_wall_left( self.grid, left, botton )
            line_right  = Util.check_wall_right( self.grid, right, botton )

            hidden_state, output = self.perceptron.run([ player.position[0], player.position[1], line_top, line_botton, line_left, line_right  ], player.weights1, player.weights2)             
            A = np.array(output)
            H = np.array(hidden_state)
            hidden = np.where(H==max(hidden_state))[0][0]
            action = np.where(A==max(output))[0][0] 

            if  (player.position[1] * player.reward) >= self.better_count :
                self.index         = player.index
                self.better_count  = (player.position[1] * player.reward)

            if(player.index == self.index) :                                          
                self.neuron_action = [hidden, action]
                self.lines_action  = [line_top, line_botton, line_left, line_right]

            if not DEBUG :                 
                Util.action_reliase(player,action)           
            
        if(self.score > MAX_TIME) :
            self.score_timeout = 0

            print('start genoma')
            self.better = Genome.get_better(self.better, self.player_list )                        
            print('end genoma')

            count_final = 0
            while len(self.player_list) > 0:                
                for player in self.player_list:  
                    if (player.position[1] * player.reward) >= self.better_count :
                        count_final += 1    
                    player.kill() 

            print('follow', count_final)
            print('startnewgame') 
            self.better_count = 0 
            self.startnewgame()                       

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player_list[0].change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_list[0].change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_list[0].change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_list[0].change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_list[0].change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_list[0].change_x = 0 

def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()