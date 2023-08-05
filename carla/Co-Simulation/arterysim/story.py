import storyboard as sb
import timeline

def createStories(board):
    time0 = sb.TimeCondition(timeline.seconds(1))
    story = sb.Story(time0, [sb.SignalEffect("traction loss")])
    board.registerStory(story)