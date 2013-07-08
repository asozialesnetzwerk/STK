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
require_once('include/Server.class.php');
require_once('include/User.class.php');
require_once('include/XMLOutput.class.php');

$action = isset($_POST['action']) ? $_POST['action'] : null;
$output = new XMLOutput();
$output->startDocument('1.0','UTF-8');

try {
    switch ($action)
    {
        case 'connect':
            try {
                $password = isset($_POST['password']) ? utf8_encode($_POST['password']) : null;
                $username = isset($_POST['username']) ? utf8_encode($_POST['username']) : null;
                $session = ClientSession::create($username, $password);
                $output->startElement('connect');
                $output->writeAttribute('success','yes');
                $output->writeAttribute('token', $session->getSessionId());
                $output->writeAttribute('username', htmlspecialchars($username));
                $output->writeAttribute('userid', $session->getUserID());
                $output->writeAttribute('info','');
                $output->endElement();
                
            }
            catch(Exception $e){
                $output->startElement('connect');
                    $output->writeAttribute('success','no');
                    $output->writeAttribute('info',
                        htmlspecialchars(
                            $e->getMessage()
                        ));
                $output->endElement();
            }

            break;
            
        case 'get_servers':
            try {
                $userid = isset($_POST['userid']) ? $_POST['userid'] : null;
                $token = isset($_POST['token']) ? $_POST['token'] : null;
                $servers_xml = Server::getServersAsXML($userid,$token);
                $output->startElement('get_servers');
                    $output->writeAttribute('success','yes');
                    $output->writeAttribute('info','');
                    $output->insert($servers_xml);
                $output->endElement();          
            }
            catch(Exception $e){
                $output->startElement('servers');
                $output->writeAttribute('success','no');
                $output->writeAttribute('info',
                    htmlspecialchars(
                        $e->getMessage()
                    ));
                $output->endElement();
            }
            
            break;
            
        case 'disconnect':
            try {
                $userid = isset($_POST['userid']) ? $_POST['userid'] : null;
                $token = isset($_POST['token']) ? $_POST['token'] : null;
                ClientSession::destroy($token, $userid);
                $output->startElement('disconnect');
                    $output->writeAttribute('success','yes');
                    $output->writeAttribute('info','');
                $output->endElement();
            }
            catch(Exception $e){
                $output->startElement('disconnect');
                    $output->writeAttribute('success','no');
                    $output->writeAttribute('info',
                        htmlspecialchars(
                            $e->getMessage()
                        ));
                $output->endElement();
            }
            break;

        case 'register':
            try {
                $username = isset($_POST['username']) ? utf8_encode($_POST['username']) : null;
                $password = isset($_POST['password']) ? utf8_encode($_POST['password']) : null;
                User::register( $username,
                                $password,
                                $password);
                $output->startElement('registration');
                    $output->writeAttribute('success','yes');
                    $output->writeAttribute('info','');
                $output->endElement();
            }
            catch(Exception $e){                                
                $output->startElement('registration');
                    $output->writeAttribute('success','no');
                    $output->writeAttribute('info',
                        htmlspecialchars(
                            $e->getMessage()
                        ));
                $output->endElement();
            }
            break;
            
        case 'create_server':
            try {
                $userid = isset($_POST['userid']) ? $_POST['userid'] : null;
                $token = isset($_POST['token']) ? $_POST['token'] : null;
                $server_name = isset($_POST['name']) ? utf8_encode($_POST['name']) : null;
                $max_players = isset($_POST['max_players']) ? $_POST['max_players'] : null;
                $server = Server::create(   $userid,
                                            $token,
                                            $server_name,
                                            $max_players);              
                $output->startElement('server_creation');
                    $output->writeAttribute('success','yes');
                    $output->writeAttribute('id', $server->getId());
                    $output->writeAttribute('name', htmlspecialchars($server->getName()));
                    $output->writeAttribute('max_players', htmlspecialchars($server->getMaxPlayers()));
                    $output->writeAttribute('info','');
                $output->endElement();
                
            }
            catch(Exception $e){
                $output->startElement('server_creation');
                    $output->writeAttribute('success','no');
                    $output->writeAttribute('info', 
                        htmlspecialchars(
                            $e->getMessage()
                        ));
                $output->endElement();
            }
            break;

        default:
            $output->startElement('request');
                $output->writeAttribute('success','no');
                $output->writeAttribute('info',
                    htmlspecialchars(
                        _('Invalid action.')
                    ));
            $output->endElement();
            break;
    }
}
catch (Exception $e) {
    $output->startElement('request');
        $output->writeAttribute('success','no');
        $output->writeAttribute('info',
            htmlspecialchars(
                _('An unexptected error occured.') .' '. 
                _('Please contact a website administrator.')
            ));
    $output->endElement();
}

$output->endDocument();
$output->printToScreen();
?>
