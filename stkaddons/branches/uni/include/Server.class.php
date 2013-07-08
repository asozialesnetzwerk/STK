<?php
/**
 * copyright 2013 Glenn De Jonghe
 *
 * This file is part of SuperTuxKart
 *
 * stkaddons is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * stkaddons is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with stkaddons.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once('exceptions.php');
require_once('DBConnection.class.php');
require_once('ClientSession.class.php');

class ServerException extends Exception {}

/**
 * Server class
 */
class Server
{
    protected $server_id;
    protected $host_id;
    protected $server_name;
    protected $max_players;

    protected function __construct($server_id, $host_id, $name, $max_players)
    {
        $this->server_id = $server_id;
        $this->host_id = $host_id;
        $this->server_name = $name;
        $this->max_players = $max_players;
    }
    
    public function getServerId()
    {
        return $this->server_id;
    }
    
    public function getHostId()
    {
        return $this->host_id;
    }
    
    public function getName()
    {
        return $this->server_name;
    }
    
    public function getMaxPlayers()
    {
        return $this->max_players;
    }
    
    /**
     * Create server
     * @param 
     * @param 
     * @return Server
     * @throws 
     */
    public static function create(  $userid,
                                    $token,
                                    $server_name,
                                    $max_players)
    {
        $max_players = (int) $max_players;
        $session = ClientSession::get($token,$userid);
        $result = DBConnection::get()->query
        (
            "INSERT INTO `" . DB_PREFIX ."servers` (hostid, name, max_players)
            VALUES (:hostid, :name, :max_players)",
            DBConnection::ROW_COUNT,
            array
            (
                ':hostid'       => (string) $session->getUserId(),
                ':name'         => (string) $server_name,
                ':max_players'  => (int)    $max_players
            )
        );
        if ($result != 1) {
            throw new ClientSessionConnectException(_('Could not create server'));
        }
        return new Server(  DBConnection::get()->lastInsertId(),
                            $session->getUserId(),
                            $server_name, 
                            $max_players);
    }
    
    public static function getServersAsXML()
    {
        $servers = DBConnection::get()->query
        (
            "SELECT (id, name, max_players, current_players)
            FROM `" . DB_PREFIX ."servers`",
            DBConnection::FETCH_ALL
        );   
        $partial_output = new XMLOutput();
        $partial_output->startElement('servers');
        foreach ($servers as $server)
        {
            $partial_output->startElement('server');
            foreach ($server as $key => $value)
                $partial_output->writeAttribute(key, value);
            $partial_output->endElement();
        }
        $partial_output->endElement();
        return $partial_output->asString();
    }
}

?>
