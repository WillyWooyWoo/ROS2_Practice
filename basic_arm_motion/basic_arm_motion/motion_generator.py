import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class MotionGenerator(Node):
    def __init__(self):
        super().__init__('motion_generator')
        
        # Publish to the /joint_states topic [cite: 184]
        self.publisher_ = self.create_publisher(JointState, 'joint_states', 10)
        
        # Run a timer loop every 50 milliseconds [cite: 185]
        self.timer = self.create_timer(0.05, self.timer_callback)
        
        # Match these exactly to the joint names in your basic_arm.urdf
        self.joint_names = ['arm_0_joint', 'arm_1_joint', 'arm_2_joint', 'gripper_1_joint', 'gripper_2_joint']
        
        # Define 5 points in the joint space to move between [cite: 191]
        self.waypoints = [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [1.0, 0.5, -0.5, 0.015, 0.015],
            [-1.0, 1.0, 0.5, 0.03, 0.03],
            [0.5, -1.0, -1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0]
        ]
        
        self.current_wp_idx = 0
        self.transition_time = 2.0  # seconds to transition between waypoints
        self.time_in_transition = 0.0
        
    def timer_callback(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        
        # Calculate how far along the current transition we are (0.0 to 1.0)
        alpha = self.time_in_transition / self.transition_time
        
        # Identify the start waypoint and the next waypoint [cite: 193]
        wp_start = self.waypoints[self.current_wp_idx]
        next_idx = (self.current_wp_idx + 1) % len(self.waypoints)
        wp_end = self.waypoints[next_idx]
        
        # Linear interpolation for smooth movement [cite: 190, 192]
        interpolated_positions = []
        for i in range(len(self.joint_names)):
            pos = wp_start[i] + alpha * (wp_end[i] - wp_start[i])
            interpolated_positions.append(pos)
            
        msg.position = interpolated_positions
        self.publisher_.publish(msg)
        
        # Advance the time clock
        self.time_in_transition += 0.05
        
        # Loop to the next waypoint when the transition is finished [cite: 193]
        if self.time_in_transition >= self.transition_time:
            self.time_in_transition = 0.0
            self.current_wp_idx = next_idx

def main(args=None):
    rclpy.init(args=args)
    node = MotionGenerator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
