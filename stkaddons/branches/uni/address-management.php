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

define('ROOT', './');
require_once('config.php');
require_once('include/ClientSession.class.php');
require_once('include/User.class.php');

$action = isset($_POST['action']) ? $_POST['action'] : null;

try {
    switch ($action)
    {
        case 'set':
            try {
                $id = isset($_POST['id']) ? utf8_encode($_POST['id']) : null;
                $token = isset($_POST['token']) ? utf8_encode($_POST['token']) : null;
                $address = isset($_POST['address']) ? utf8_encode($_POST['address']) : null;
                $port = isset($_POST['port']) ? utf8_encode($_POST['port']) : null;
                ClientSession::setPublicAddress($id, $token, $address, $port);

                returnXML('<address-management success="yes" />');
            }
            catch(Exception $e){
                returnXML('<address-management success="no" info="' . $e->getMessage() . '"/>');
            }
            break;
        case 'start-server':
            try {
                $id = isset($_POST['id']) ? utf8_encode($_POST['id']) : null;
                $token = isset($_POST['token']) ? utf8_encode($_POST['token']) : null;
                $address = isset($_POST['address']) ? utf8_encode($_POST['address']) : null;
                $port = isset($_POST['port']) ? utf8_encode($_POST['port']) : null;
                ClientSession::get($token, $id)->createServer($address, $port, "Temporary name", 3);
                
                returnXML('<address-management success="yes" />');
            }
            catch(Exception $e){
                returnXML('<address-management success="no" info="' . $e->getMessage() . '"/>');
            }
            break;
        case 'stop-server':
            try {
                $id = isset($_POST['id']) ? utf8_encode($_POST['id']) : null;
                $token = isset($_POST['token']) ? utf8_encode($_POST['token']) : null;
                $address = isset($_POST['address']) ? utf8_encode($_POST['address']) : null;
                $port = isset($_POST['port']) ? utf8_encode($_POST['port']) : null;
                ClientSession::get($token, $id)->stopServer($address, $port);
                
                returnXML('<address-management success="yes" />');
            }
            catch(Exception $e){
                returnXML('<address-management success="no" info="' . $e->getMessage() . '"/>');
            }
            break;
        case 'unset':
            try {
                $id = isset($_POST['id']) ? utf8_encode($_POST['id']) : null;
                $token = isset($_POST['token']) ? utf8_encode($_POST['token']) : null;
                $count = ClientSession::unsetPublicAddress($id, $token);
                if ($count == 1) {
                    returnXML('<address-management success="yes" />');
                }
                else if ($count == 0) {
                    returnXML('<address-management success="no" info="ID:Token must be wrong."/>');
                }
                else {
                    returnXML('<address-management success="no" info="Weird count of updates."/>');
                }
            }
            catch(Exception $e){
                returnXML('<address-management success="no" info="' . $e->getMessage() . '"/>');
            }
            break;
        case 'get':
            try {
                $id = isset($_POST['id']) ? utf8_encode($_POST['id']) : null;
                $token = isset($_POST['token']) ? utf8_encode($_POST['token']) : null;
                $peer_id = isset($_POST['peer_id']) ? utf8_encode($_POST['peer_id']) : null;
                $session = ClientSession::get($token, $id);
                $result = $session->getPeerAddress($peer_id);
                returnXML('<address-management success="yes" 
                            ip="'.$result['ip'].'" port="'.$result['port'].'" />');
            }
            catch(Exception $e){
                returnXML('<address-management success="no" info="' . $e->getMessage() . 
                        '"/>');
            }
            break;
        case 'request-connection':
            try {
                $id = isset($_POST['id']) ? utf8_encode($_POST['id']) : null;
                $token = isset($_POST['token']) ? utf8_encode($_POST['token']) : null;
                $server_id = isset($_POST['server_id']) ? utf8_encode($_POST['server_id']) : null;
                ClientSession::get($token, $id)->requestServerConnection($server_id);
                returnXML('<address-management success="yes" />');
            }
            catch(Exception $e){
                returnXML('<address-management success="no" info="' . $e->getMessage() . 
                        '"/>');
            }
            break;
        case 'poll-connection-requests':
            try {
                $id = isset($_POST['id']) ? utf8_encode($_POST['id']) : null;
                $token = isset($_POST['token']) ? utf8_encode($_POST['token']) : null;
                $result = ClientSession::get($token, $id)->getServerConnectionRequests();
                $ret = "";
                foreach ($result as $row) {
                    $ret .= '<user id="'.$row['userid'].'" /> ';
                } 
                returnXML("<users> ".$ret." </users>");
            }
            catch(Exception $e){
                returnXML('<address-management success="no" info="' . $e->getMessage() . 
                        '"/>');
            }
            break;

        default:
            returnXML('<address-management success="no" info="' . 
                htmlspecialchars(_('Invalid action.')) . 
                '"/>');
            break;
    }
}
catch (Exception $e) {
    returnXML('<request success="no" info="' . 
        htmlspecialchars(_('An unexptected error occured.') .' '. _('Please contact a website administrator.')) . 
        '"/>');
}


function returnXML($xml)
{
    ob_start();
    header('Content-type: text/xml');
    echo '<?xml version="1.0"?>\n';
    echo $xml;
    ob_end_flush();
}
?>
