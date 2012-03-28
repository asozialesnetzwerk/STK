<div id="content">
    <?php
    if (isset($error_msg)) {
        echo '<span class="error">';
        if (is_array($error_msg)) {
            foreach ($error_msg as $field => $msg) {
                echo HTML::chars($msg).'<br />';
            }
        }
        else {
            echo HTML::chars($error_msg);
        }
        echo '</span><br />';
    }
    ?>

    <?php echo Form::open(); ?>
    <?php echo Form::label('user', I18n::get('Username:')); ?><br />
    <?php echo Form::input('user', $form_user); ?><br />
    <?php echo Form::label('pass', I18n::get('Password:')); ?><br />
    <?php echo Form::password('pass'); ?><br />
    <?php echo Form::submit(NULL, I18n::get('Log In')); ?>
    <?php echo Form::close(); ?>

    <a href="<?php echo URL::site('user/register'); ?>"><?php echo HTML::chars(I18n::get('Create an account.')); ?></a><br />
    <a href="<?php echo URL::site('user/reset_password'); ?>"><?php echo HTML::chars(I18n::get('Forgot password?')); ?></a>
</div>
