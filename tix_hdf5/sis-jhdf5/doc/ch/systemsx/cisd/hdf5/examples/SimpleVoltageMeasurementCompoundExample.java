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

import ch.systemsx.cisd.hdf5.HDF5Factory;
import ch.systemsx.cisd.hdf5.IHDF5SimpleWriter;

/**
 * This is a simple example which demonstrates reading and writing of a "compound" data set that
 * stores a temperature / voltage measurement point.
 */
public class SimpleVoltageMeasurementCompoundExample
{

    /**
     * A Data Transfer Object for a combined temperature / voltage measurement.
     */
    static class Measurement
    {
        Date date;

        float temperature;

        double voltage;

        // Important: needs to have a default constructor, otherwise JHDF5 will bail out on reading.
        Measurement()
        {
        }

        Measurement(Date date, float temperature, double voltage)
        {
            this.date = date;
            this.temperature = temperature;
            this.voltage = voltage;
        }

        @Override
        public String toString()
        {
            return "Measurement [date=" + date + ", temperature=" + temperature + ", voltage="
                    + voltage + "]";
        }

    }

    public static void main(String[] args)
    {
        // Open "singleVoltageMeasurement.h5" for writing
        IHDF5SimpleWriter hdf5Writer = HDF5Factory.open("singleVoltageMeasurement.h5");

        // Write a measurement
        hdf5Writer.writeCompound("measurement", new Measurement(new Date(), 18.6f, 15.38937516));

        // See what we've written out
        System.out.println("Compound measurement record: "
                + hdf5Writer.readCompound("measurement", Measurement.class));

        // Close the HDF5 writer
        hdf5Writer.close();
    }

}
