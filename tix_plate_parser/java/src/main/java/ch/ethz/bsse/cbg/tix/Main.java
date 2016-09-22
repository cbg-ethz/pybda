package ch.ethz.bsse.cbg.tix;

import ch.ethz.bsse.cbg.tix.parser.TixParser;
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

    @Option(name = "-f", usage = "path to the plate folder", required = true, metaVar = "FILE")
    private String _plateFolder;

    @Option(name = "-m", usage = "the meta-discription of sirna-hugo mappings", required = true, metaVar = "META")
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
        new TixParser(_plateFolder, _metaFile).parse();
    }

    private void parseArgs(String[] args)
    {

        CmdLineParser parser = new CmdLineParser(this);
        try
        {
            parser.parseArgument(args);
        }
        catch (CmdLineException e)
        {
            _LOGGER.error("Could not parse command line arguments! Exiting!");
            System.err.println(e.getMessage() + "\n");
            System.err.print("USAGE: ");
            System.err.println("java -jar tixParser.jar [options]");
            parser.printUsage(System.err);
            System.exit(-1);
        }
    }
}
