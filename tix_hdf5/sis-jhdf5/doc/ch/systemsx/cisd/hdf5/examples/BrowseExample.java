/*
 * Copyright 2011 ETH Zuerich, CISD
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ch.systemsx.cisd.hdf5.examples;

import java.util.Date;
import java.util.List;

import ch.systemsx.cisd.hdf5.HDF5DataSetInformation;
import ch.systemsx.cisd.hdf5.HDF5Factory;
import ch.systemsx.cisd.hdf5.HDF5LinkInformation;
import ch.systemsx.cisd.hdf5.IHDF5Reader;
import ch.systemsx.cisd.hdf5.IHDF5Writer;

/**
 * Example for browsing the content of an HDF5 file.
 */
public class BrowseExample
{

    static void browse(IHDF5Reader reader, List<HDF5LinkInformation> members, String prefix)
    {
        for (HDF5LinkInformation info : members)
        {
            System.out.println(prefix + info.getPath() + ":" + info.getType());
            switch (info.getType())
            {
                case DATASET:
                    HDF5DataSetInformation dsInfo = reader.object().getDataSetInformation(info.getPath());
                    System.out.println(prefix + "     " + dsInfo);
                    break;
                case SOFT_LINK:
                    System.out.println(prefix + "     -> " + info.tryGetSymbolicLinkTarget());
                    break;
                case GROUP:
                    browse(reader, reader.object().getGroupMemberInformation(info.getPath(), true),
                            prefix + "  ");
                    break;
                default:
                    break;
            }
        }
    }

    public static void main(String[] args)
    {
        // Create an HDF5 file we can browse.
        IHDF5Writer writer = HDF5Factory.configure("browsing.h5").overwrite().writer();
        writer.object().createGroup("groupA");
        writer.object().createGroup("groupB");
        writer.object().createGroup("groupA/groupC");
        writer.string().write("/groupA/string", "Just some random string.");
        writer.int32().writeArray("/groupB/inarr", new int[]
            { 17, 42, -1 });
        writer.float64().writeMatrix("/groupB/dmat", new double[][]
            {
                { 1.1, 2.2, 3.3 },
                { 4.4, 5.5, 6.6 },
                { 7.7, 8.8, 9.9 }, });
        writer.object().createSoftLink("/groupA/groupC", "/groupB/groupC");
        writer.time().write("/groupA/date", new Date());
        writer.close();

        // Browse it.
        IHDF5Reader reader = HDF5Factory.openForReading("browsing.h5");
        browse(reader, reader.object().getGroupMemberInformation("/", true), "");
        reader.close();
    }

}
