    <?php if ( isset($mini_survey) ) {
        if ( $mini_survey['show'] ) { ?>
                <form class="minisurvey" method="post" action="<?=OPTION_SURVEY_URL?>">
                    <p>Did you find what you were looking for?</p>
                    <input type="hidden" name="sourceidentifier" value="twfy-mini-2">
                    <input type="hidden" name="datetime" value="<?= $mini_survey['datetime'] ?>">
                    <input type="hidden" name="subgroup" value="0">
                    <input type="hidden" name="user_code" value="<?= $mini_survey['user_code'] ?>">
                    <input type="hidden" name="auth_signature" value="<?= $mini_survey['auth_signature'] ?>">
                    <input type="hidden" name="came_from" value="<?= $mini_survey['page_url'] ?>">
                    <input type="hidden" name="return_url" value="<?= $mini_survey['page_url'] ?>">
                    <input type="hidden" name="question_no" value="<?= $mini_survey['current_q'] ?>">
                    <ul>
                        <li><label><input type="radio" name="find_on_page" value="1"> Yes</label></li>
                        <li><label><input type="radio" name="find_on_page" value="0"> No</label></li>
                    </ul>

                    <input type="submit" value="Submit answer">
                </form>
        <?php } else if ( $mini_survey['answered'] ) { ?>
            <p>Thanks for answering</p>
        <?php } ?>
    <?php } ?>
