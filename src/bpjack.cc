
#include "bpjack.h"
#include "boost/python.hpp"

using namespace std;

vector<string> 
JackPort::get_all_connections()
{
    vector<string> retval;

    const char ** conns = jack_port_get_all_connections( _client->cl(), _port );
    if (conns == 0)
        return retval;

    for (int i=0; conns[i]; i++)
    {
        retval.push_back( string(conns[i]) );
    }

    jack_free( conns );

    return retval;
}

JackSessionCommand::JackSessionCommand( jack_session_command_t *cmd )
    : uuid(cmd->uuid)
    , clientname(cmd->client_name)
    , command(cmd->command)
    , flags(flags)
{ }

string
JackPort::name()
{
    return string( jack_port_name( _port ) );
}

std::string 
JackPort::type()
{
    return string( jack_port_type( _port ) );
}

int 
JackPort::flags()
{
    return jack_port_flags( _port );
}

JackPort::JackPort( boost::shared_ptr<JackClient> client, jack_port_t *port )
    : _port(port)
    , _client(client)
{ }

JackClientSingleton::JackClientSingleton( const std::string & name )
{
    _client = jack_client_open( name.c_str(), JackNullOption, NULL );
    jack_set_port_registration_callback( _client, JackClientSingleton::port_reg_cb_aux, this );
    jack_activate( _client );
}

JackClientSingleton::~JackClientSingleton()
{
    jack_client_close( _client );
}

std::string 
JackClientSingleton::pop_port()
{
    boost::unique_lock<boost::mutex> guard( _queue_lock );

    if (_port_queue.empty())
        _queue_cond.wait( guard );

    string retval = _port_queue.front();
    _port_queue.pop();
    return retval;
}

void
JackClientSingleton::port_reg_cb_aux( jack_port_id_t port_id, int reg, void *arg )
{
    JackClientSingleton * single = static_cast<JackClientSingleton *> ( arg );
    single->port_reg_cb( port_id, reg );
}

void
JackClientSingleton::port_reg_cb( jack_port_id_t port_id, int reg )
{
    if (reg)
    {
        jack_port_t * p = jack_port_by_id( _client, port_id );
        string name = jack_port_name( p );
        boost::unique_lock<boost::mutex> guard( _queue_lock );
        _port_queue.push( name );
        _queue_cond.notify_one();
    }
}

boost::shared_ptr<JackClient> JackClient::create( const std::string & name )
{
    boost::shared_ptr<JackClientSingleton> singleton( new JackClientSingleton( name ) );
    return boost::shared_ptr<JackClient>( new JackClient(singleton) );
}

void JackClient::activate()
{
    jack_activate( _client );
}

void JackClient::deactivate()
{
    jack_deactivate( _client );
}

std::vector<std::string> 
JackClient::get_ports()
{
    vector<string> retval;

    const char ** ports = jack_get_ports( _client, 0, 0, 0 );
    if (ports == 0)
        return retval;

    for (int i=0; ports[i]; i++)
    {
        retval.push_back( string(ports[i]) );
    }

    jack_free( ports );

    return retval;
}

JackPort 
JackClient::port_by_name( const std::string & name )
{
    jack_port_t *port = jack_port_by_name( _client, name.c_str() );
    return JackPort( shared_from_this(), port );
}

int 
JackClient::reserve_client_name( const std::string & name, const std::string & uuid )
{
    return jack_reserve_client_name( _client, name.c_str(), uuid.c_str() );
}

std::vector<JackSessionCommand> 
JackClient::session_notify( const std::string & target, int type, const std::string & path )
{
    vector<JackSessionCommand> retval;
    jack_session_command_t *cmds = jack_session_notify( _client, target.c_str(), (jack_session_event_type_t) type, path.c_str() );
    if (cmds == 0)
        return retval;

    for (int i=0; cmds[i].uuid != 0; i++)
        retval.push_back( JackSessionCommand(& cmds[i]) );

    jack_session_commands_free( cmds );
    return retval;
}

std::vector<JackSessionCommand> 
JackClient::session_notify_any( int type, const std::string & path )
{
    vector<JackSessionCommand> retval;
    jack_session_command_t *cmds = jack_session_notify( _client, NULL, (jack_session_event_type_t) type, path.c_str() );
    if (cmds == 0)
        return retval;

    for (int i=0; cmds[i].uuid != 0; i++)
        retval.push_back( JackSessionCommand(& cmds[i]) );

    jack_session_commands_free( cmds );
    return retval;
}
std::string 
JackClient::get_client_name_by_uuid( const std::string & uuid )
{
    return string( jack_get_client_name_by_uuid (_client, uuid.c_str()) );
}

int 
JackClient::connect( const std::string & src, const std::string & dst)
{
    return jack_connect( _client, src.c_str(), dst.c_str() );
}

int 
JackClient::disconnect( const std::string & src, const std::string & dst )
{
    return jack_disconnect( _client, src.c_str(), dst.c_str() );
}

JackClient::JackClient( boost::shared_ptr<JackClientSingleton> singleton )
{
    _client = singleton->cl();
    _singleton = singleton;
}



BOOST_PYTHON_MODULE(bpjack)
{
    using namespace boost::python;

    def( "create_client", &JackClient::create );
    const string & (vector<string>::*vsat)(size_t)const              = &vector<string>::at;
    const JackSessionCommand & (vector<JackSessionCommand>::*vcat)(size_t)const              = &vector<JackSessionCommand>::at;


    class_<vector<string> >("string_vec", no_init)
        .def( "__len__", &vector<string>::size )
        .def( "__getitem__", vsat, return_value_policy<copy_const_reference>() );

    class_<vector<JackSessionCommand> >("cmd_vec", no_init)
        .def( "__len__", &vector<JackSessionCommand>::size )
        .def( "__getitem__", vcat, return_value_policy<copy_const_reference>() );

    class_<JackSessionCommand>("JackSessionCommand", no_init)
        .def_readonly( "uuid", &JackSessionCommand::uuid )
        .def_readonly( "clientname", &JackSessionCommand::clientname )
        .def_readonly( "commandline", &JackSessionCommand::command )
        .def_readonly( "flags", &JackSessionCommand::flags );

    class_<JackPort, boost::shared_ptr<JackPort> >("JackPort", no_init)
        .def("get_all_connections", &JackPort::get_all_connections)
        .def("name", &JackPort::name)
        .def("type", &JackPort::type)
        .def("flags", &JackPort::flags);
        
    class_<JackClient, boost::shared_ptr<JackClient> >("JackClient", no_init)
        .def("activate",        &JackClient::activate )
        .def("deactivate",      &JackClient::deactivate )
        .def("port_by_name",    &JackClient::port_by_name )
        .def("get_ports",       &JackClient::get_ports )
        .def("session_notify",  &JackClient::session_notify )
        .def("session_notify_any",  &JackClient::session_notify_any )
        .def("get_client_name_by_uuid", &JackClient::get_client_name_by_uuid )
        .def("reserve_client_name", &JackClient::reserve_client_name )
        .def("connect", &JackClient::connect )
        .def("disconnect", &JackClient::disconnect )
        .def("pop_port", &JackClient::pop_port );
}
