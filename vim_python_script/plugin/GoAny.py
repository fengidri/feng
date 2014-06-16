#encoding:utf8
from gatekeeper import gatekeeper 
import pyvim
import flog
import frain_libs.paths_exp as paths_exp
import os
import vim
import vhc_protocol

class GoAny( pyvim.command ):
    def run( self ):


        gate = gatekeeper( )
        gate.reg_to_vhc( )
        gate.just_req( "/GoAnyUi/start" )
        cur_file = vim.current.buffer.name
        while True:
            res = gate.response( )
            if res.is_req( ):
                url = res.url( )
                flog.loginfo( "url:%s" % url )

                res_to_goany = vhc_protocol.response( vhc_protocol.GoAnyUi )
                if url.startswith( "/Vim/GoAnyUi/init" ):
                    
                    flog.loginfo( "TagFile:%s" % cur_file)
                    tags = get_file_tag( cur_file )
                    #gate.req_with_data( "GoAnyUi", tags )
                    res_to_goany.set_data( tags )
                    res_to_goany.add_data( "current_file", cur_file )
                    res_to_goany.add_data( "current_target", "file_fun" )

                elif url.startswith( "/Vim/GoAnyUi/file_fun" ):
                    file_path = res.get_data( )
                    flog.loginfo( "TagFile:%s" % file_path)
                    tags = get_file_tag( file_path )
                    res_to_goany.set_data( tags )
                    #gate.req_with_data( "GoAnyUi", tags )
                    res_to_goany.add_data( "current_target", "file_fun" )
                    

                elif url.startswith( "/Vim/GoAnyUi/file" ):

                    files = paths_exp.get_files( )

                    res_to_goany.set_data( files )
                    res_to_goany.add_data( "current_file", cur_file )
                    res_to_goany.add_data( "current_target", "file" )
                else:
                    continue

                gate.send( res_to_goany.dump_data() )


            else:
                break
        file_path= res.get_data( )[ 0 ]
        line_nu = res.get_data( )[ 1 ]
        if file_path and file_path != cur_file :
            vim.command( "update" )
            vim.command( "silent edit %s" % file_path)

        if line_nu :
            vim.current.window.cursor = ( line_nu, 0 )








def get_file_tag( file_name ):
    all_var = [  ]
    if not file_name:
        return all_var
    cmd = "ctags -f - -n --fields=-lzf %s" % file_name
    f = os.popen( cmd )

    for line in f.readlines( ):
        tmp = line.split( )
        keyword= tmp[0] #tag name
        keyword_type = tmp[ 3 ] # 类型如 f
        linenu = int(tmp[ 2 ][ 0: -2 ])# 行号, ctag 输出如: 114;"

        if not keyword_type in "fm":# 只取函数名
            continue

        if len(tmp) > 4:# 最一列用于记录所属的类或结构体
            keyword = "%s.%s" % (tmp[ 4 ]  , keyword)

        all_var.append( ( 
            "%s.%s"%(keyword, keyword_type) ,  # for display
            keyword ,# for filter 
            linenu , # the value
            None
            ) )
    return all_var




