import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.CmdLineParser;
import org.kohsuke.args4j.Option;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * @author Simon Dirmeier {@literal simon.dirmeier@gmx.de}
 */
public class Main
{

    private static final Logger _LOGGER = LoggerFactory.getLogger(Main.class);

    @Option(name = "-f", usage = "path to the plate folder")
    private String _plateFolder;

    @Option(name = "-m", usage = "the meta-discription of sirna-hugo mappings")
    private String _metaFile;


    public static void main(String[] args)
    {
        setup();
        new Main().run(args);
    }

    private static void setup()
    {
        org.apache.log4j.ConsoleAppender appender = new org.apache.log4j.ConsoleAppender();
        appender.setWriter(new java.io.OutputStreamWriter(java.lang.System.out));
        appender.setLayout(new org.apache.log4j.PatternLayout("%-5p [%t]: %m%n"));
        org.apache.log4j.Logger.getRootLogger().addAppender(appender);
    }

    private void run(String[] args)
    {
        parseArgs(args);
        System.out.println(_plateFolder);
        System.out.println(_metaFile);
    }

    private void parseArgs(String[] args)
    {
        try
        {
            new CmdLineParser(this).parseArgument(args);
        }
        catch (CmdLineException e)
        {
            _LOGGER.error("Could not parse command line arguments!");
            System.exit(-1);
        }
    }
}
