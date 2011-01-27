
#include <jack/jack.h>
#include <jack/session.h>
#include <boost/shared_ptr.hpp>
#include <boost/enable_shared_from_this.hpp>
#include <boost/thread/condition_variable.hpp>
#include <boost/thread/mutex.hpp>


#include <vector>
#include <string>
#include <queue>
#include <exception>

class JackClient;

class JackPort
{
    public:
        std::vector<std::string> get_all_connections();

        std::string name();
        std::string type();
        int flags();
    private:
        friend class JackClient;
        jack_port_t * _port;
        boost::shared_ptr<JackClient> _client;

        JackPort( boost::shared_ptr<JackClient> client, jack_port_t *port );
};

struct JackSessionCommand
{
    JackSessionCommand( jack_session_command_t *cmd );

    std::string uuid;
    std::string clientname;
    std::string command;
    int flags;
};

class JackClientSingleton
{
    public:
        JackClientSingleton( const std::string & name );
        ~JackClientSingleton();

        std::string pop_port();
        jack_client_t * cl() { return _client; }
        void abort_monitor();

    private:
        jack_client_t *_client;
	boost::mutex _queue_lock;
        boost::condition_variable _queue_cond;
        std::queue<std::string> _port_queue;
        bool _abort;

        static void port_reg_cb_aux( jack_port_id_t port_id, int reg, void *arg );
        void port_reg_cb( jack_port_id_t port_id, int reg );
};

class JackClient : public boost::enable_shared_from_this<JackClient>
{
    public:
        static boost::shared_ptr<JackClient> create( const std::string & name );

        void activate();
        void deactivate();

        std::vector<std::string> get_ports();

        JackPort port_by_name( const std::string & name );
        int reserve_client_name( const std::string & name, const std::string & uuid );

        std::vector<JackSessionCommand> session_notify( const std::string & target, int type, const std::string & path );
        std::vector<JackSessionCommand> session_notify_any( int type, const std::string & path );
	int client_has_session_callback( const std::string & name );

        std::string get_client_name_by_uuid( const std::string & uuid );

        int connect( const std::string & src, const std::string & );
        int disconnect( const std::string & src, const std::string & );

        jack_client_t * cl() { return _client; }

        std::string pop_port() { return _singleton->pop_port(); }
        void abort_monitor() { _singleton->abort_monitor(); }

    private:
        JackClient( boost::shared_ptr<JackClientSingleton> singleton );
        boost::shared_ptr<JackClientSingleton> _singleton;
        jack_client_t *_client;

};


class NoJackClientException : public std::exception
{
    public:
	NoJackClientException () {}
	virtual ~NoJackClientException() throw() {}

	virtual const char * what() const throw() { return (char *) "Cant create JackClient"; }
};

