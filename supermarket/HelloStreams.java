package space;

import com.fasterxml.jackson.databind.JsonNode;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.connect.json.JsonDeserializer;
import org.apache.kafka.connect.json.JsonSerializer;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.kstream.*;

import java.util.Properties;
import java.util.concurrent.CountDownLatch;

public class HelloStreams {

    public static void main(String[] args) throws InterruptedException {
        // Configure the Kafka Streams application
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "filter-cash-payments");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");

        // Define the JSON SerDe
        final JsonSerializer jsonSerializer = new JsonSerializer();
        final JsonDeserializer jsonDeserializer = new JsonDeserializer();
        final Serde<JsonNode> jsonSerde = Serdes.serdeFrom(jsonSerializer, jsonDeserializer);

        // Create a StreamsBuilder
        StreamsBuilder builder = new StreamsBuilder();

        // Create a KStream from the supermarket_purchases topic
        KStream<String, JsonNode> sourceStream = builder.stream("supermarket_purchases", Consumed.with(Serdes.String(), jsonSerde));

        // Filter messages where payment_method is 'cash'
        KStream<String, JsonNode> filteredStream = sourceStream.filter(
                (key, jsonNode) -> jsonNode.get("payment_method").asText().equals("cash")
        );

        // Print the filtered messages to the console
        filteredStream.print(Printed.toSysOut());

        // Write the filtered messages to the cash_payments topic
        filteredStream.to("cash_payments", Produced.with(Serdes.String(), jsonSerde));

        Topology topology = builder.build();
        // Visualize the topology
        System.out.println("On this page you can visualize the topology: https://zz85.github.io/kafka-streams-viz/");
        System.out.println(topology.describe());

        // We need a latch here, because the Kafka Streams application is running in a separate thread.
        CountDownLatch latch = new CountDownLatch(1);


        // Build and start the Kafka Streams application
        try (KafkaStreams streams = new KafkaStreams(topology, props)) {
            // Add shutdown hook to gracefully close the streams application
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                latch.countDown();
                streams.close();
            }));
            streams.start();
            latch.await();

        }
    }
}
