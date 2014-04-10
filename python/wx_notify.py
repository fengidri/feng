#encoding:utf8
import wx
import time
import thread
class Notify_ui( wx.Frame ):
    def __init__( self, notify , app):
        self.app = app
        wx.Frame.__init__( self, 
                None, 
                -1, 
                "Notify", 
                size=(400, 40),
                style=wx.FRAME_SHAPED |
                          wx.SIMPLE_BORDER |
                          wx.FRAME_NO_TASKBAR |
                          wx.STAY_ON_TOP
                )

        self.SetTransparent( 20 )

        panel = wx.Panel( self , -1 )
        panel.SetBackgroundColour(wx.Colour(147, 145, 145))
        panel.SetTransparent( 20 )



        self.Centre(  )

        width, height = self.GetSize()
        bmp = wx.EmptyBitmap(width,height)

        dc = wx.BufferedDC(None, bmp)
        dc.BeginDrawing()
        dc.SetBackground(wx.Brush(wx.Colour(0,0,0), wx.SOLID))
        dc.Clear()
        dc.DrawRoundedRectangle(0, 0, width-1, height-1, 12)
        dc.EndDrawing()

        r = wx.RegionFromBitmapColour(bmp, wx.Colour(0,0,0))
        self.hasShape = self.SetShape(r)

        wx.StaticText( panel, -1, notify, 
                (100, 10) )
        wx.CallAfter( self.close_notify, 0)
    def close_notify( self, i ):
        time.sleep( 2 )
        self.Destroy( )
        return
        self.app.Destroy( )
        self.app.ExitMainLoop( )
        time.sleep( 1 )
        self.Exit( )
        self.Destroy( )
        self.Close( )

def __run( text ):
    app = wx.App( )
    frame = Notify_ui( text, app )
    frame.Show( )
    
    app.MainLoop( )

def notify( text):
    thread.start_new_thread( __run, (text,))



