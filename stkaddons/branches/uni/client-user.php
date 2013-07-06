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
        case 'connect':
            try {
                $password = isset($_POST['password']) ? utf8_encode($_POST['password']) : null;
                $username = isset($_POST['username']) ? utf8_encode($_POST['username']) : null;
                $session = ClientSession::create($username, $password);
                returnXML('<connect success="yes" 
                                    token="'. $session->getSessionId() . '"
                                    username="' . $session->getUserName() . '"
                                    userid="' . $session->getUserID() . '"                                     
                />');
                
            }
            catch(Exception $e){
                returnXML('<connect success="no" info="' . $e->getMessage() . '"/>');
            }

            break;

        case 'disconnect':
            try {
                $userid = isset($_POST['userid']) ? utf8_encode($_POST['userid']) : null;
                $token = isset($_POST['token']) ? $_POST['token'] : null;
                ClientSession::destroy($token, $userid);
                returnXML('<disconnect success="yes"/>');
            }
            catch(Exception $e){
                returnXML('<disconnect success="no" info="' . $e->getMessage() . ' "/>');
            }
            break;

        case 'register':
            try {
                $username = isset($_POST['username']) ? utf8_encode($_POST['username']) : null;
                $password = isset($_POST['password']) ? utf8_encode($_POST['password']) : null;
                User::register( $username,
                                $password,
                                $password);
                returnXML('<registration success="yes" info=""/>');
            }
            catch(Exception $e){
                returnXML('<registration success="no" info="' . $e->getMessage() . ' "/>');
            }
            break;

        default:
            returnXML('<request success="no" info="' . 
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
