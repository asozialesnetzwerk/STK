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
define('API', 1);
require_once(ROOT . 'config.php');
require_once(ROOT . 'include/ClientSession.class.php');
require_once(ROOT . 'include/Server.class.php');
require_once(ROOT . 'include/User.class.php');
require_once(ROOT . 'include/XMLOutput.class.php');

$action = isset($_POST['action']) ? $_POST['action'] : "";
$output = new XMLOutput();
$output->startDocument('1.0','UTF-8');

try {
    switch ($action)
    {
        case 'connect':
            try {
                $password = isset($_POST['password']) ? utf8_encode($_POST['password']) : "";
                $username = isset($_POST['username']) ? utf8_encode($_POST['username']) : "";
                $session = ClientSession::create($username, $password);
                $output->startElement('connect');
                $output->writeAttribute('success','yes');
                $output->writeAttribute('token', $session->getSessionID());
                $output->writeAttribute('username', htmlspecialchars($session->getUsername()));
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
            
        case 'saved-session':
            try {
                $userid = isset($_POST['userid']) ? $_POST['userid'] : "";
                $token = isset($_POST['token']) ? $_POST['token'] : "";
                $session = ClientSession::get($token, $userid);
                User::updateLoginTime($session->getUserID());
                $output->startElement('saved-session');
                $output->writeAttribute('success','yes');
                $output->writeAttribute('token', $session->getSessionID());
                $output->writeAttribute('username', htmlspecialchars($session->getUsername()));
                $output->writeAttribute('userid', $session->getUserID());
                $output->writeAttribute('info','');
                $output->endElement();
                
            }
            catch(Exception $e){
                $output->startElement('saved-session');
                    $output->writeAttribute('success','no');
                    $output->writeAttribute('info',
                        htmlspecialchars(
                            $e->getMessage()
                        ));
                $output->endElement();
            }

            break;
            
        case 'get_server_list':
            try {
                $servers_xml = Server::getServersAsXML();
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
                $userid = isset($_POST['userid']) ? $_POST['userid'] : "";
                $token = isset($_POST['token']) ? $_POST['token'] : "";
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
            
        case 'create_server':
            try {
                $userid = isset($_POST['userid']) ? $_POST['userid'] : "";
                $token = isset($_POST['token']) ? $_POST['token'] : "";
                $server_name = isset($_POST['name']) ? utf8_encode($_POST['name']) : "";
                $max_players = isset($_POST['max_players']) ? $_POST['max_players'] : "";
                $server = ClientSession::get($token, $userid)->createServer(0, 0, $server_name, $max_players);           
                $output->startElement('server_creation');
                    $output->writeAttribute('success','yes');
                    $output->writeAttribute('info','');
                    $output->insert($server->asXML());
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
            
        case 'register':
            try {
                $username           = isset($_POST['username']) ? utf8_encode($_POST['username']) : "";
                $password           = isset($_POST['password']) ? utf8_encode($_POST['password']) : "";
                $password_confirm   = isset($_POST['password_confirm']) ? utf8_encode($_POST['password_confirm']) : "p";
                $email              = isset($_POST['email']) ? utf8_encode($_POST['email']) : "";
                $terms              = isset($_POST['terms']) ? utf8_encode($_POST['terms']) : "";
                User::register( $username,
                                $password,
                                $password_confirm,
                                $email,
                                $username,
                                $terms);
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
                
        case 'recovery':
            try {
                $username           = isset($_POST['username']) ? utf8_encode($_POST['username']) : "";
                $email              = isset($_POST['email']) ? utf8_encode($_POST['email']) : "";

                User::recover( $username, $email);
                $output->startElement('recovery');
                $output->writeAttribute('success','yes');
                $output->writeAttribute('info','');
                $output->endElement();
            }
            catch(Exception $e){
                $output->startElement('recovery');
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
