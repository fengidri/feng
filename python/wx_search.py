#encoding:utf8
import wx
import fuzzy
"""
 适合于在一个list 中快速找到自己想要的内容
"""
class ListBox( wx.ListBox ):
    def __init__( self, panel, src_list ):

        wx.ListBox.__init__(self, panel, -1, 
                (15, 50), (410, 320), src_list, 
                wx.LB_SINGLE)
        self.SetSelection(0)

class Enter( wx.TextCtrl ):
    def __init__( self, panel, listbox, frame ):
        wx.TextCtrl.__init__(self,
                panel,
                -1, 
               u'',
               (15, 20),
               size=(410, 22),
               style=wx.TE_PROCESS_ENTER 
               )
        self.SetInsertionPoint(0)
        self.Bind( wx.EVT_TEXT, self.event_text)
        self.Bind( wx.EVT_TEXT_ENTER, self.event_enter)
        #self.Bind( wx.EVT_KEY_DOWN, self.event_key_down)
        self.listbox = listbox
        self.frame = frame
        self.src_list = frame.src_list
        self.res_value = frame.res_value
    def event_key_down( self, event):
        key =  event.GetKeyCode( )
        if key == 317:#down
            index = self.listbox.GetSelection( )
            self.listbox.SetSelection(index + 1)
            return 0

        if key == 315:#up
            index = self.listbox.GetSelection( )
            if index > 0:
                self.listbox.SetSelection(index - 1)
            return 0
    def event_enter( self, event):#按下回车
        value = self.listbox.GetStringSelection( )
        index = self.listbox.GetSelection( )
        self.res_value.append( (index,value) )
        self.frame.Destroy( )
        return 0

    def event_text( self, event ):#内容发生变化
        #key =  event.GetKeyCode( )
        #print key
        #try:
        #    char = chr( key )
        #except:
        #    char = None
        #if key > 300:
        #    return 0

        #if key == 27 :#esc
        #    self.frame.Destroy( )
        #    return 0

        #if key == 13:

        patten = self.GetValue( )
        tmp = patten.split( ":" )
        if len( tmp ) > 1:
            if tmp[-1].isdigit( ):
                index =  int( tmp[-1] ) - 1
                self.listbox.SetSelection( index )
        else:

            self.listbox.Clear( )

            print patten
            for line in self.src_list:
                if fuzzy.diffuse( patten, line ):
                    self.listbox.Append( line )
            try:
                self.listbox.SetSelection(0)
            except :
                pass

class TextFrame(wx.Frame):
    def __init__(self, src_list, res_value):
        """
         res_value 用于保存返回值
        """
        self.res_value = res_value
        self.src_list = src_list
        wx.Frame.__init__(self, None, -1, 'Text Entry Example', 
                size=(440, 400),
                style=wx.FRAME_SHAPED |
                          wx.SIMPLE_BORDER |
                          wx.FRAME_NO_TASKBAR |
                          wx.STAY_ON_TOP
                )

        self.Center( )

        panel = wx.Panel(self, -1)


        self.listbox = ListBox( panel, src_list )
        self.enter = Enter( panel, self.listbox, self  )




def search( src_list ):
    res=[  None ]

    app = wx.App()
    frame = TextFrame( src_list, res )
    frame.Show()

    app.MainLoop()

    return res[ -1 ]


if __name__ == "__main__":
    sampleList = ['zero', 'one', 'two', 'three', 'four', 'five',
                      'six', 'seven', 'eight', 'nine', 'ten', 'eleven',
                      'twelve', 'thirteen', 'fourteen']
    print search( sampleList )

