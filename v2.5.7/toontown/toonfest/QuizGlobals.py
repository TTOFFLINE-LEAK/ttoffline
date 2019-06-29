

class Question:

    def __init__(self, question, rightAns, wrongAns):
        self.question = question
        self.rightAns = rightAns
        self.wrongAns = wrongAns


CATEGORY_COGS = 1
CATEGORY_PLAYGROUND = 2
CATEGORY_MINIGAMES = 3
CATEGORY_GAGS = 4
CATEGORY_TOONS = 5
CATEGORY_OTHER = 6
CategoryIdToName = {CATEGORY_COGS: 'the Cogs', 
   CATEGORY_PLAYGROUND: 'Playgrounds', 
   CATEGORY_MINIGAMES: 'minigames', 
   CATEGORY_GAGS: 'gags', 
   CATEGORY_TOONS: 'famous Toons', 
   CATEGORY_OTHER: 'miscellaneous'}
QuestionsDict = {CATEGORY_COGS: [
                 Question('What is the first Cog most Toons will fight?', ['Flunky'], [
                  'The Chairman', 'Bean Counter', 'Bottom Feeder', 'Tightwad', 'Downsizer'])], 
   CATEGORY_PLAYGROUND: [
                       Question('Where could you find Goofy before racing?', ['Daisy Gardens'], [
                        'Goofy Speedway', 'Funny Farm', 'Toontown Central', 'The Brrrgh', 'Construction Zone'])], 
   CATEGORY_MINIGAMES: [
                      Question('Which of the following games can you not play alone?', [
                       'Race Game', 'Trolley Tracks', 'Match Minnie', 'Toon Tag'], [
                       'Jungle Vines', 'Photo Fun', 'Toon Memory Game', 'Five Nights at the Factory', 'Tug-of-War'])], 
   CATEGORY_GAGS: [
                 Question('Which of the following does the least damage?', ['Small Magnet', 'Presentation', '$1 Bill'], [
                  'Cream Pie Slice', 'Bike Horn', 'Banana Peel', 'Geyser', 'Flower Pot'])], 
   CATEGORY_TOONS: [
                  Question('Who is the PR Lead for Toontown Rewritten?', ['Sir Max'], [
                   'Slate Blue Rabbit', 'OtakuSRL', 'roger dog', 'Sparkpin', 'Rocky', 'Smirky Bumberpop'])], 
   CATEGORY_OTHER: [
                  Question('When did Toontown Online close?', ['Sept. 19, 2013'], [
                   'Oct. 28, 2013', 'Sept. 9, 2013', 'June 2, 2003', 'Oct. 21, 2002', 'Never'])]}