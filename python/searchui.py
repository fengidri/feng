#encoding:utf8
#!/usr/bin/python
import pickle
import Tkinter as tk

#esc 退出 默认
class Search( object ):
    def __init__( self, des_list=None, filte=None, pre= None ):
        self.root=tk.Tk( )
        root = self.root

        #root.overrideredirect( 1 )

        self.des_list = des_list
        self.des_list.append( None )
        self.filte = filte


        self.root.title( "Vim Py")
        self.center( self.root, 500, 300)

        self.enterframe = tk.Frame(root)
        self.enterframe.pack(fill=tk.X)

        self.listframe = tk.Frame(root)
        self.listframe.pack(fill=tk.BOTH, expand=1)


        self.enter =  tk.Entry(self.enterframe,
                bg="white",
                font="Monaco 10  ",
                )
        self.enter.focus( )
        self.enter.bind("<Return>", self.quit_enter )
        self.enter.bind("<KeyRelease>", self.on_enter )
        #self.enter.bind("<Key>", self.on_keypress )

        #self.enter.bind("<Control-j>", self.list_down )
        #self.enter.bind("<Control-k>", self.list_up )

        self.listbox = tk.Listbox(self.listframe, 
                bd=1,
                bg="white",
                font="Monaco 10  ",
                selectmode=tk.SINGLE
                )
        self.listbox.bind( )
        if isinstance(pre, list):
            for line in pre:
                self.listbox.insert(tk.END, line)


        self.listbox.bind("<Double-Button-1>", self.quit_list)
        self.enter.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.listbox.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)

        lines = self.filte( "" )
        if isinstance( lines, list):
            for line in lines:
                self.listbox.insert(tk.END, line)

            #激活第一个对象
            self.listbox.selection_set( 0 )
        self.root.mainloop( )

    def center( self, root, width=None, height=None ):
        root.update( )
        if width==None:
            curWidth= root.winfo_reqwidth( )
        else:
            curWidth = width
        if height==None:
            curHeight= root.winfo_height( )
        else:
            curHeight= height
        scnWidth, scnHeight = root.maxsize( )
        tmpcnf = "%dx%d+%d+%d"%( 
                curWidth,curHeight,
                 (scnWidth-curWidth)/2,(scnHeight-curHeight)/2
                )
        root.geometry( tmpcnf )
    def list_up( self, event):
            index = self.listbox.curselection(  )[ 0 ]
            self.listbox.select_clear( index )
            self.listbox.selection_set( index - 1 )
    def list_down( self, event):
            index = self.listbox.curselection(  )[ 0 ]
            self.listbox.select_clear( index )
            self.listbox.selection_set( index + 1 )
    def on_keypress( self, event):
        if event.keycode == 9: #ESC 退出
            self.root.destroy( )
            return 0

        if event.keycode == 116:#down
            index = self.listbox.curselection(  )[ 0 ]
            self.listbox.select_clear( index )
            self.listbox.selection_set( index + 1 )
            return 

        if event.keycode == 115:#up
            index = self.listbox.curselection(  )[ 0 ]
            self.listbox.select_clear( index )
            self.listbox.selection_set( index - 1 )
            return 

    def on_enter(self, event):
        #每按一个键进行处理

        self.listbox.delete( 0, self.listbox.size() )

        contents = self.enter.get()
        
        lines = self.filte( contents )
        if not isinstance( lines, list):
            return 0

        for line in lines:
            self.listbox.insert(tk.END, line)

        #激活第一个对象
        self.listbox.selection_set( 0 )

    def quit_enter( self, event ):
        #回车退出
        listbox = self.listbox
        if listbox.size( ) >  0:
            index = self.listbox.curselection(  )[ 0 ]
            res = self.listbox.get(index )

            self.des_list.append( [ index, res] )

        self.root.destroy( )
    
    def quit_list( self, event):
        #双击list item 退出
        self.des_list.append( self.listbox.get(tk.ANCHOR))
        self.root.destroy( )
if __name__ == "__main__":
    def fi( patt ):
        lines = open( "/home/feng/ab.py" ).readlines( )
    
        res = [  ]
        for line in lines:
            if line.find( patt )> -1:
                res.append( line )
        return res
    
    rs =[  ]
    s=Search( rs, fi)
    print rs.pop( )
