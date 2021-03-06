<?php

namespace MySociety\TheyWorkForYou\SectionView;

class LordsView extends SectionView {
    protected $major = 101;
    protected $class = 'LORDSDEBATELIST';

    protected function front_content() {
        return $this->list->display('biggest_debates', array('days'=>7, 'num'=>20), 'none');
    }
}
