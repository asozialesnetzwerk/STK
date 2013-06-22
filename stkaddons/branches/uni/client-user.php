<?php
/**
 * copyright 2013
 *
 * This file is part of stkaddons
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
include_once('config.php');
include_once('include/ClientSession.class.php');
include_once('include/User.class.php');

$action = isset($_POST['action']) ? $_POST['action'] : null;
$user = isset($_POST['user']) ? utf8_encode($_POST['user']) : null;

try {
    switch ($action)
    {
        case 'connect':
            try {
                $password = isset($_POST['password']) ? utf8_encode($_POST['password']) : null;
                $session = ClientSession::create($user, $password);
                returnXML('<connect success="yes" 
                                    token="'. $session->getSessionId() . '"
                                    username="' . $session->getName() . '"                                     
                />');
                
            }
            catch(Exception $e){
                returnXML('<connect success="no" info="' . $e->getMessage() . ' "/>');
            }

            break;

        case 'disconnect':
            try {
                $token = isset($_POST['token']) ? $_POST['token'] : null;
                ClientSession::destroy($token, $user);
                returnXML('<disconnect success="yes"/>');
            }
            catch(Exception $e){
                returnXML('<disconnect success="no" info="' . $e->getMessage() . ' "/>');
            }
            break;

        case 'register':
            try {
                $password = isset($_POST['password']) ? utf8_encode($_POST['password']) : null;
                User::register($user,$password,$password);
                returnXML('<registration success="yes"/>');
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
