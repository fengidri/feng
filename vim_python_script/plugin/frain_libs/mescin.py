#encoding:utf8
import os
import json

home = os.environ[ "HOME" ]

config_dir = os.path.join(home, '.config/mescin')
runtime_dir = os.path.join( config_dir, '.runtime' )

class _SrcPathConfig( object ):
    def __init__( self, src_path ):
        self.path = src_path.get( "path", "" )
        self.name = src_path.get( "name" )
        if not self.name:
            self.name =  os.path.basename( self.path )

class _SrcPathConfigList( list ):
    def __init__( self, _list = [] ):
        for src_path in _list:
            self.append( _SrcPathConfig(src_path) )

class _CompileConfig( object ):
    def __init__( self, _dict = {} ):
        self.path = _dict.get( "path" )
        pass
        

class _ProConfig( object ):
    name = str
    src_path = _SrcPathConfigList
    compile_info = _CompileConfig

# 说明: 配置文件对象
#     对应于一个配置文件
class ProConfig( _ProConfig ):
    def __init__( self, json_path ):
        self.cfg_file_path = None
        self.load( json_path )
        pass
    def load( self, json_path ):
        class_attrs = _ProConfig.__dict__

        json_context = open( json_path ).read( )
        json_obj = json.loads( json_context )
        json_keys = json_obj.keys( )

        for attr, value in class_attrs.items( ):
            if attr.startswith( "__" ):
                continue
            if attr in json_keys:
                setattr( self, attr, value(json_obj[attr])  )
            else:
                setattr( self, attr, value()  )


# Runtime 信息对象
class RuntimeConfig( object ):
    def __init__( self, json_path="", name="" ):
        self.last_opens = ""
        self.sync_time = ""
        self.name = ""
        self.json_path = ""

        if name and not json_path:
            """
                初始化一个对象, 要提供name
            """
            self.name = name
            self.json_path = os.path.join( runtime_dir, self.name  + ".json")
            self.sync_time = 0
        if json_path:
            """
                通过json_path 载入一个对象
            """
            self.json_path = json_path
            self.load( json_path )

    def load( self, json_path ):
        json_context = open( json_path ).read( )
        json_obj = json.loads( json_context )

        self.name = json_obj[ "name" ]
        self.last_opens = json_obj.get( "last_open" ,"")
        self.sync_time = json_obj.get( "sync_time", 0)

    def dumps( self ):
        json_runtime = {  }
        json_runtime[ "name" ] = self.name
        json_runtime[ "last_open" ] = self.last_opens
        json_runtime[ "sync_time" ] = self.sync_time
        return json_runtime

    def save( self ):
        f =  open( self.json_path, 'w')
        f.write( json.dumps(self.dumps() ,sort_keys=True, indent = 4) )
        f.close( )





# 说明: 配置文件对象管理
#     管理所有的配置文件
class ProConfigs( object ):
    def __init__( self ):
        self.configs = [  ]
        self.runtime = [  ]
        
        cfg_files = os.listdir( config_dir )

        for cfg_file_name in cfg_files:
            if not cfg_file_name.endswith( ".json" ):
                continue
            cfg_file_path = os.path.join( config_dir, cfg_file_name )
            self.configs.append( ProConfig(cfg_file_path) )
            
            

        runtime_files = os.listdir( runtime_dir )

        for runtime_file_name in runtime_files:
            if not runtime_file_name.endswith( ".json" ):
                continue
            runtime_file_path = os.path.join( runtime_dir, runtime_file_name )
            self.runtime.append( RuntimeConfig(json_path = runtime_file_path) )

    def get_by_name( self, name ):
        "get cfg and runtime by name"
        
        _cfg = None
        _runtime = None
        for cfg in self.configs:
            if cfg.name == name:
                _cfg = cfg
                break
        for runtime in self.runtime:
            if runtime.name == name:
                _runtime = runtime
                break
        if _runtime == None and _cfg != None:
            """
                有cfg 文件, 但是没有runtime 文件, 初始化一个runtime 对象
            """
            _runtime = RuntimeConfig( name = _cfg.name )
        return _cfg, _runtime
    def get_info_for_select( self ):
        info = [  ]
        for cfg in self.configs:
            if not cfg.src_path:
                continue
            name = cfg.name
            root = cfg.src_path[0].path
            dispaly = ("%s (%s)" % (name, root))

            info.append( (dispaly, name, None, None) )
        return info



Config = None
def init(  ):
    global Config
    if Config:
        return
    Config = ProConfigs( )
