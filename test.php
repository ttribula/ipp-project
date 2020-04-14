<?php

class Arguments {
    public $testDir = './';
    public $recursive = 0;
    public $parsePath = './parse.php';
    public $interpretPath = './interpret.py';
    public $parseOnly = 0;
    public $intOnly = 0;
    public $jexamxmlPath = '/pub/courses/ipp/jexamxml/jexamxml.jar';



    public function __construct() {
        global $argc;
        $allowed_options = array(
            'help',
            'directory:',
            'recursive',
            'parse-script:',
            'int-script:',
            'parse-only',
            'int-only',
            'jexamxml:'
        );
        $opts = getopt(null,$allowed_options);

        if (isset($opts['help'])) {
            if ($argc != 2){
                fwrite(STDERR, "CHYBA: Nespravne zadane argumenty souboru test.php:
                    Argument help nesmi byt pouzit s dalsimi argumenty.");
            }
            print "Tento skript slouzi pro automaticke testovani skriptu parse.php a interpret.py.\n".
                "Pouziti:\n".
                    "php7.4 test.php [--help] [--directory=TESTS_PATH] [--recursive] [--parse-script=PATH_TO_PARSE_SKRIPT] ".
                    "[--int-script=PATH_TO_INTERPRET_SKRIPT] [--parse-only] [--int-only] [--jexamxml=PATH_TO_JEXAMXML]\n";
            exit(0);
        }
        if (isset($opts['directory'])) {
            $this->testDir = $opts['directory'];
            if (substr($this->testDir, -1) != '/')
                $this->testDir = $this->testDir."/";
        }
        if (isset($opts['recursive'])) {
            $this->recursive = 1;
        }
        if (isset($opts['parse-script'])) {
            $this->parsePath = $opts['parse-script'];
        }
        if (isset($opts['int-script'])) {
            $this->interpretPath = $opts['int-script'];
        }
        if (isset($opts['parse-only']) and !(isset($opts['int-script']) or isset($opts['int-only']))) {
            $this->parseOnly = 1;
        }
        if (isset($opts['int-only']) and !(isset($opts['parse-script']) or isset($opts['parse-only']))) {
            $this->intOnly = 1;
        }
        if (isset($opts['jexamxml'])) {
            $this->jexamxmlPath = $opts['jexamxml'];
        }
    }
}

class Test {
    private $arguments;
    private $stats;
    private $output;
    public $total_stats;
    public function __construct() {
        $this->arguments = new Arguments();
        $this->stats = array();
        $this->output = array();
        $this->total_stats['Total'] = 0;
        $this->total_stats['Passed'] = 0;
        $this->total_stats['Error'] = 0;

        $this->check_dir($this->arguments->testDir);
    }

    public function check_dir($dir) {
        if (!file_exists($dir)) {
            fwrite(STDERR, "CHYBA: Zadany soubor neexistuje.");
            exit(11);
        }

        $stat_index = count($this->stats);
        $this->stats[$stat_index]['Dir_name'] = $dir;
        $this->stats[$stat_index]['Total'] = 0;
        $this->stats[$stat_index]['Passed'] = 0;
        $this->stats[$stat_index]['Error'] = 0;
        $all_files = scandir($dir);
        foreach ($all_files as $file) {
            if (is_file($dir.$file)){
                if (preg_match('~\.src$~', $file)) {
                    $this->testFile($file, $dir, $stat_index);

                }
            } elseif (is_dir($dir.$file)) {
                if ($this->arguments->recursive) {
                    if ($file == '.' || $file == '..') {
                        continue;
                    }
                    $this->check_dir($dir.$file."/");
                }
            }

        }
    }

    public function testFile($file, $dir, $stat_index) {
        $file = substr($file, 0, -4);

        $absolute_path = $dir.$file;

        if (!file_exists($absolute_path.".in")) {
            if (!touch($absolute_path.".in")) {
                fwrite(STDERR, "CHYBA: $absolute_path.in soubor chybi a nelze vytvorit novy.");
                exit(12);
            }
        }
        if (!file_exists($absolute_path.".out")) {
            if (!touch($absolute_path.".out")) {
                fwrite(STDERR, "CHYBA: $absolute_path.out soubor chybi a nelze vytvorit novy.");
                exit(12);
            }
        }
        if (!file_exists($absolute_path.".rc")) {
            if (!($rc = fopen($absolute_path.".rc", "w"))) {
                fwrite(STDERR, "CHYBA: $absolute_path.rc soubor chybi a nelze vytvorit novy.");
                exit(12);
            }
        fwrite($rc, "0");
        fclose($rc);
        }


        if (!($rc = fopen($absolute_path.".rc", 'r'))) {
            fwrite(STDERR, "CHYBA: Nepodarilo se otevrit soubor $absolute_path.rc\n");
        }
        $return_code = (int) trim(fgets($rc));
        fclose($rc);
        $rc = 'ERROR';
        $out = 'ERROR';
        if ($this->arguments->parseOnly) {
            exec("php7.4 ".$this->arguments->parsePath." <$absolute_path.src >parse_tmp_out 2>/dev/null", $parse_out, $parse_rc);
            if ($return_code == $parse_rc) {
                $rc = 'OK';

                exec("java -jar ".$this->arguments->jexamxmlPath." $parse_out $absolute_path.out /D", $dump, $parse_diff_rc);
                if ($parse_diff_rc == 0) {
                    $out = 'OK';
                }
            }
            unlink("parse_tmp_out");
        } elseif ($this->arguments->intOnly) {
            exec("timeout 5s python3.8 ".$this->arguments->interpretPath." --input=\"$absolute_path.in\" --source=\"$absolute_path.src\" >int_tmp_out 2>/dev/null", $int_out, $int_rc);
            if ($return_code == $int_rc) {
                $rc = 'OK';
                exec("diff int_tmp_out $absolute_path.out >diff_file", $dump, $int_diff_rc);
                if ($int_diff_rc == 0) {
                    $out = 'OK';
                }
            }
            exec("rm int_tmp_out");
        } else {
            exec("php7.4 ".$this->arguments->parsePath." <$absolute_path.src >parse_tmp_out 2>/dev/null", $parse_out, $parse_rc);
            if ($parse_rc == 0) {
                exec("timeout 5s python3.8 ".$this->arguments->interpretPath." --input=\"$absolute_path.in\" --source=\"parse_tmp_out\" >int_tmp_out 2>/dev/null", $int_out, $int_rc);
                if ($return_code == $int_rc) {
                    $rc = 'OK';
                    exec("diff int_tmp_out $absolute_path.out >diff_file", $dump, $int_diff_rc);
                    if ($int_diff_rc == 0) {
                        $out = 'OK';
                    }
                }
                exec("rm int_tmp_out");
            }
            exec("rm parse_tmp_out");

        }


        $this->output[$stat_index][] = array($file, $out, $rc);
        $this->stats[$stat_index]['Total']++;
        $this->total_stats['Total']++;
        if ($rc == 'OK' && $out == 'OK') {
            $this->stats[$stat_index]['Passed']++;
            $this->total_stats['Passed']++;
        } else {
            $this->stats[$stat_index]['Error']++;
            $this->total_stats['Error']++;
        }
    }

    public function print_stats() {
        if (count($this->stats) == 0) {
            return;
        }

        $stat_index = 0;
        foreach ($this->stats as $stat) {?>
            <div class="stat">
                <h3>Adresar: "<?php echo $stat['Dir_name'];?>"</h3>
                <p>Celkem v adresari testovano <?php echo $stat['Total']?>, <?php echo $stat['Passed']?> uspesnych, <?php echo $stat['Error']?> neuspesnych</p>
                <?php
                if(!isset($this->output[$stat_index])) {
                    $stat_index++;
                    continue;
                }
                ?>
                <table>
                    <tr>
                        <th>Jmeno testu</th>
                        <th>Vystup</th>
                        <th>Navratovy kod</th>
                    </tr>
                        <?php

                    foreach ($this->output[$stat_index] as $out) {
                        ?>
                        <tr>
                            <td class="result" id="<?php echo $out[0]; ?>"><?php echo $out[0]; ?></td>
                            <td class="result" id="<?php echo $out[1]; ?>"><?php echo $out[1]; ?></td>
                            <td class="result" id="<?php echo $out[2]; ?>"><?php echo $out[2]; ?></td>
                        </tr>
                    <?php
                    }
                    ?>
                </table>
            </div>
            <?php
            $stat_index++;
        }
    }

}
$test = new Test();
?>
<!DOCTYPE HTML>
<html lang="cs">
	<head>
		<meta charset="utf-8" />
		<style>
            .stat {
                float: left;
            }
            #OK
            {
                background-color: green;
            }

            #ERROR
            {
                background-color: red;
            }
		</style>
		<title>Vysledky testu test.php.</title>
	</head>
	<body>
		<div class="container">
			<div class="header">
				<h1>Vysledky testu test.php</h1>
                <h2>Celkem testu: <?php echo $test->total_stats['Total']; ?><br>
                    Uspesnych: <?php echo $test->total_stats['Passed']; ?><br>
                    Neuspesnych: <?php echo $test->total_stats['Error']; ?></h2>
			</div>
			<div class="content">
				<?php
                    $test->print_stats();
                ?>
			</div>
		</div>
	</body>
</html>
<?php
exit(0);