<?php defined('SYSPATH') or die('No direct script access.');

/**
 * Asset flags (bit masks)
 *
 * Do not change existing flags! Doing so will cause errors with existing
 * add-ons and possibly game incompatibility. To add new flags, create a
 * new constant and set it to the next power of 2.
 * The current database schema allows 24 flags.
 */
final class AssetFlags {

    public static $approved = 1;
    public static $alpha = 2;
    public static $beta = 4;
    public static $rc = 8;
    public static $invisible = 16;
    public static $reserved = 32;
    public static $dfsg = 64;
    public static $featured = 128;
    public static $latest = 256;
    public static $tex_not_power_of_2 = 512;
}
