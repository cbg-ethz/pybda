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

import ch.systemsx.cisd.hdf5.HDF5Factory;
import ch.systemsx.cisd.hdf5.IHDF5Reader;
import ch.systemsx.cisd.hdf5.IHDF5Writer;

/**
 * Example for using HDF5 attributes. Attributes are kind of annotations of the dataset. They
 * shouldn't be used for large data themselves.
 */
public class AttributeExample
{

    public static void main(String[] args)
    {
        // Write a String dataset.
        IHDF5Writer writer = HDF5Factory.configure("attribute.h5").writer();
        writer.string().write("a string", "Just some random string.");
        // Set two attributes on it.
        writer.bool().setAttr("a string", "important", false);
        writer.time().setAttr("a string", "timestamp", System.currentTimeMillis());
        writer.close();

        // Read the dataset and the attributes.
        IHDF5Reader reader = HDF5Factory.openForReading("attribute.h5");
        System.out.println(reader.string().read("a string"));
        System.out.println(reader.bool().getAttr("a string", "important"));
        System.out.println(reader.time().getAttr("a string", "timestamp"));
        reader.close();
    }

}
