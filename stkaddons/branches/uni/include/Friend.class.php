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

require_once(ROOT . 'include/exceptions.php');
require_once(ROOT . 'include/DBConnection.class.php');
require_once(ROOT. 'include/XMLOutput.class.php');


class FriendException extends Exception {}

/**
 * Server class
 */
class Friend
{
    protected $is_asker;
    protected $friend_id;
    protected $date;
    protected $is_pending;

    /**
     * 
     * @param array $info_array an associative array based on the database
     */
    protected function __construct($info_array)
    {
		$this->info_array = $info_array;
    }
    
    public function getFriendId()
    {
        return $this->info_array['friend_id'];
    }
    
    public function getDate()
    {
        return $this->info_array['date'];
    }
    
    public function isPending()
    {
        return $this->info_array['request'] === 1;
    }
    
    public function isAsker()
    {
        return $this->info_array['is_asker'] === 1;
    }
    
    public function asXML()
    {
    	$friend_xml = new XMLOutput();
	    $friend_xml->startElement('friend');
	    foreach ($this->info_array as $key => $value)
	    	$friend_xml->writeAttribute($key, $value);
	    $friend_xml->endElement();
	    return $friend_xml->asString();
    }
    
    /**
     * Create server
     * @param 
     * @param 
     * @return Server
     * @throws 
     *//*
    public static function create(  $ip,
                                    $port,
                                    $userid,
                                    $server_name,
                                    $max_players)
    {
        $max_players = (int) $max_players;
        try{
            $count = DBConnection::get()->query
            (
                "SELECT `id` FROM `" . DB_PREFIX . "servers`
                    WHERE `ip`= :ip AND `port`= :port ",
                DBConnection::ROW_COUNT,
                array
                (
                    ':ip'   => $ip,
                    ':port' => $port
                )
            );
            if ($count != 0)
                throw new ServerException(_('Specified server already exists.'));
            $result = DBConnection::get()->query
            (
                "INSERT INTO `" . DB_PREFIX ."servers` (hostid, ip, port, name, max_players)
                VALUES (:hostid, :ip, :port, :name, :max_players)",
                DBConnection::ROW_COUNT,
                array
                (
                    ':hostid'       => (int) $userid,
                    ':ip'           => (int) $ip,
                    ':port'         => (int) $port,
                    ':name'         => (string) $server_name,
                    ':max_players'  => (int)    $max_players
                )
            );
            if ($result != 1) {
                throw new ServerException(_('Could not create server'));
            }
            return Server::getServer(DBConnection::get()->lastInsertId());

        }catch(PDOExpcetion $e){
            throw new ServerException(
                _('An error occurred while creating server.') .' '.
                _('Please contact a website administrator.')
            );
        }
    }*/
    
    /**
     * Returns XML string
     * @param int $userid
     * @return string
     */
    public static function getFriendsAsXML($userid)
    {
        $friends = DBConnection::get()->query
        (
            "SELECT date, request, asker_id AS friend_id, 0 AS is_asker FROM `" . DB_PREFIX ."friends` WHERE receiver_id = :userid
            UNION
            SELECT date, request, receiver_id AS friend_id, 1 AS is_asker FROM `" . DB_PREFIX ."friends` WHERE asker_id = :userid
            ORDER BY date DESC",
            DBConnection::FETCH_ALL,
            array
            (
                ':userid'       => (int) $userid
            )          
        );
        $partial_output = new XMLOutput();
        $partial_output->startElement('friends');
        foreach ($friends as $friend_result)
        {
        	$friend = new Friend($friend_result);
            $partial_output->insert($friend->asXML());
        }
        $partial_output->endElement();
        return $partial_output->asString();
    }
}

?>
