## import the library
#from appJar import gui

## handle button events
#def press(button):
#    if button == "Cancel":
#        app.stop()
#    else:
#        app2 = app.startSubWindow('Demo')
#        app.addNamedButton("CLOSE", "Demo", app.hideSubWindow)
#        print(app2.title)
#        app.showSubWindow('Demo')

## create a GUI variable called app
#app = gui("autopod")
#app.addButton('Goto app2',press)
#tools = ['SEARCH PODS','REMOVE POD','DISPLAY PODS']
#def tbfuncs(tb):
#    print(tb)
#
#app.addToolbar(tools, tbfuncs,findIcon=True)
#app.go()

from appJar import gui 

def launch(win):
    app.showSubWindow(win)

app=gui()

# this is a pop-up
app.startSubWindow("one", modal=True)
app.addLabel("l1", "SubWindow One")
app.stopSubWindow()

# this is another pop-up
app.startSubWindow("two")
app.addLabel("l2", "SubWindow Two")
app.stopSubWindow()

# these go in the main window
app.addButtons(["one", "two"], launch)

app.go()
