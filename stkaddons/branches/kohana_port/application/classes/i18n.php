<?php
/**
 * Internationalization using gettext
 */
class I18n {
    /**
     * @var string target language, gettext style
     */
    public static $lang = 'en_US';

    /**
     * @var type string gettext domain
     */
    public static $domain = 'translations';

    /**
     * Get and set language
     * @param string $lang set new language
     * @return string current language
     */
    public static function lang($lang)
    {
        if (!empty($lang)) {
            I18n::$lang = $lang;
            I18n::setlocale(I18n::$lang);
        }

        return I18n::$lang;
    }

    /**
     * Get translated text
     * @param string $string translate this text
     * @param type $lang target language
     */
    public static function get($string, $lang = NULL)
    {
        if (is_null($lang)) {
            return gettext($string);
        }
        else {
            I18n::setlocale($lang);
            $translation = gettext($string);
            I18n::setlocale(I18n::$lang);
            return $translation;
        }
    }

    public static function init()
    {
        I18n::setlocale(I18n::$lang);
        bindtextdomain(I18n::$domain, DOCROOT.'/locale');
        textdomain(I18n::$domain);
        bind_textdomain_codeset(I18n::$domain, 'UTF-8');
    }

    private static function setlocale($lang)
    {
        putenv("LC_ALL=$lang");
        setlocale(LC_ALL, $lang);
    }
}

// Initialize gettext
I18n::init();

// Load Kohana_I18n because it defines __ function
Kohana::auto_load('Kohana_I18n');

?>
