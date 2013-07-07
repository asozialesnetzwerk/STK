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

try {
    try {
    $id = isset($_POST['id']) ? utf8_encode($_POST['id']) : null;
    $token = isset($_POST['token']) ? utf8_encode($_POST['token']) : null;
    $address = isset($_POST['address']) ? utf8_encode($_POST['address']) : null;
    $port = isset($_POST['port']) ? utf8_encode($_POST['port']) : null;
    $count = ClientSession::setPublicAddress($id, $token, $address, $port);
    if ($count == 1) {
        returnXML('<set-public-address success="yes" />');
    }
    else if ($count == 0) {
        returnXML('<set-public-address success="no" info="ID:Token must be wrong."/>');
    }
    else {
        returnXML('<set-public-address success="no" info="Weird count of updates."/>');
    }
    }
    catch(Exception $e){
        returnXML('<set-public-address success="no" info="' . $e->getMessage() . '"/>');
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
